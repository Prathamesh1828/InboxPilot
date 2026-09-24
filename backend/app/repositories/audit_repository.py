import copy
import logging

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent
from app.models.email import Email
import json
from app.core.redis import redis_client
from sqlalchemy import or_
from datetime import datetime

logger = logging.getLogger(__name__)


def _scrub_sensitive_data(details: dict | None) -> dict | None:
    if not details:
        return details

    scrubbed = copy.deepcopy(details)
    sensitive_keys = {"token", "access_token", "refresh_token", "password", "api_key", "secret"}

    def _scrub(d: dict):
        for k, v in d.items():
            if any(sensitive in k.lower() for sensitive in sensitive_keys):
                d[k] = "***"
            elif isinstance(v, dict):
                _scrub(v)

    _scrub(scrubbed)
    return scrubbed


def log_audit_event(
    db: Session,
    email_id: int,
    event_type: str,
    action: str | None = None,
    status: str | None = None,
    details: dict | None = None,
    approval_id: int | None = None,
) -> None:
    """
    Log an audit event for an email workflow.
    This operation is failure-safe. It will not raise an exception if it fails.
    """
    try:
        scrubbed_details = _scrub_sensitive_data(details)

        event = AuditEvent(
            email_id=email_id,
            approval_id=approval_id,
            event_type=event_type,
            action=action,
            status=status,
            details=scrubbed_details,
        )

        db.add(event)
        db.commit()
        db.refresh(event)
        
        # Publish real-time event to the specific user's channel
        try:
            email = db.query(Email).filter(Email.id == email_id).first()
            if email and email.user_id:
                event_dict = {
                    "id": event.id,
                    "email_id": event.email_id,
                    "approval_id": event.approval_id,
                    "event_type": event.event_type,
                    "action": event.action,
                    "status": event.status,
                    "details": event.details,
                    "created_at": event.created_at.isoformat()
                }
                redis_client.publish(
                    f"audit_logs:{email.user_id}",
                    json.dumps(event_dict)
                )
        except Exception as pub_exc:
            logger.error("Failed to publish audit event: %s", pub_exc)

    except Exception as exc:
        db.rollback()
        logger.error(
            "Failed to log audit event %s for email %d: %s",
            event_type,
            email_id,
            exc,
        )


def get_email_audit_events(db: Session, email_id: int) -> list[AuditEvent]:
    return (
        db.query(AuditEvent)
        .filter(AuditEvent.email_id == email_id)
        .order_by(AuditEvent.created_at.asc())
        .all()
    )


def get_all_audit_events(
    db: Session, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 50,
    event_type: str | None = None,
    action: str | None = None,
    status: str | None = None,
    search: str | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
) -> list[AuditEvent]:
    query = (
        db.query(AuditEvent)
        .join(Email, AuditEvent.email_id == Email.id)
        .filter(Email.user_id == user_id)
    )

    if event_type and event_type != "All":
        query = query.filter(AuditEvent.event_type == event_type)
    if action and action != "All":
        query = query.filter(AuditEvent.action == action)
    if status and status != "All":
        query = query.filter(AuditEvent.status == status)
    if date_from:
        query = query.filter(AuditEvent.created_at >= date_from)
    if date_to:
        query = query.filter(AuditEvent.created_at <= date_to)
        
    if search:
        search_pattern = f"%{search}%"
        query = query.filter(
            or_(
                AuditEvent.event_type.ilike(search_pattern),
                AuditEvent.action.ilike(search_pattern),
                AuditEvent.status.ilike(search_pattern),
                Email.subject.ilike(search_pattern),
                Email.sender.ilike(search_pattern),
            )
        )

    return query.order_by(AuditEvent.created_at.desc()).offset(skip).limit(limit).all()
