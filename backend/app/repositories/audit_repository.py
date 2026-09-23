import copy
import logging

from sqlalchemy.orm import Session

from app.models.audit_event import AuditEvent

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


def get_all_audit_events(db: Session, skip: int = 0, limit: int = 50) -> list[AuditEvent]:
    return (
        db.query(AuditEvent)
        .order_by(AuditEvent.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )
