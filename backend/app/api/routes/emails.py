from typing import Any
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.core.limiter import limiter
from app.models.user import User
from app.repositories.email_repository import get_emails, get_emails_by_user
from app.schemas.email import EmailCreate, EmailResponse, PaginatedEmailResponse, EmailDetailResponse
from app.services.email_service import (
    get_email,
    ingest_email,
)
from app.repositories.audit_repository import get_email_audit_events
from app.repositories.action_approval_repository import get_pending_approval_by_email_id
from app.schemas.audit import AuditEventResponse
from app.workers.tasks import process_email_pipeline


router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
    dependencies=[Depends(get_current_user)],
)


# ---------------------------------------------------------
# GET ALL EMAILS
# ---------------------------------------------------------

@router.get(
    "",
    response_model=PaginatedEmailResponse,
)
@limiter.limit("60/minute")
def read_emails(
    request: Request,
    search: str | None = None,
    category: str | None = None,
    status: str | None = None,
    confidence_min: int | None = None,
    confidence_max: int | None = None,
    date_from: str | None = None,
    date_to: str | None = None,
    sort_by: str = "received_at",
    sort_order: str = "desc",
    page: int = 1,
    limit: int = 50,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Get all emails for the authenticated user, ordered newest to oldest, with filtering and pagination.
    """

    items, total = get_emails_by_user(
        db=db,
        user_id=current_user.id,
        search=search,
        category=category,
        status=status,
        confidence_min=confidence_min,
        confidence_max=confidence_max,
        date_from=date_from,
        date_to=date_to,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit,
    )

    return {
        "items": items,
        "total": total,
        "page": page,
        "size": len(items),
    }


# ---------------------------------------------------------
# GET SINGLE EMAIL
# ---------------------------------------------------------

@router.get(
    "/{email_id}",
    response_model=EmailDetailResponse,
)
@limiter.limit("60/minute")
def read_email(
    request: Request,
    email_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single email by its database ID, enriched with workflow state.
    """

    email = get_email(
        db=db,
        email_id=email_id,
    )

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    # 1. Base response
    response_data: dict[str, Any] = {
        "id": email.id,
        "user_id": email.user_id,
        "provider_message_id": email.provider_message_id,
        "thread_id": email.thread_id,
        "sender": email.sender,
        "subject": email.subject,
        "recipients": email.recipients,
        "body": email.body,
        "received_at": email.received_at,
        "processed_at": email.processed_at,
        "created_at": email.created_at,
        "status": email.status,
        "category": email.category,
        "classification_confidence": email.classification_confidence,
        "classification_reasoning": email.classification_reasoning,
        "classified_at": email.classified_at,
    }

    # 2. Get Audit Events to reconstruct action plan state
    audit_events = get_email_audit_events(db=db, email_id=email_id)
    
    action_plan = None
    safety_result = None
    execution_result = None
    error_message = None

    for event in audit_events:
        if event.event_type == "PLAN_CREATED":
            if event.details:
                action_plan = {
                    "action": event.action,
                    "parameters": event.details.get("parameters", {}),
                    "risk_level": event.details.get("risk_level"),
                    "requires_approval": event.details.get("requires_approval"),
                }
        elif event.event_type == "SAFETY_EVALUATED":
            if event.details:
                safety_result = {
                    "action": event.action,
                    "risk_level": event.details.get("risk_level"),
                    "requires_approval": event.details.get("requires_approval"),
                }
                # Update action plan if safety modified it
                if action_plan:
                    action_plan["action"] = event.action
                    action_plan["risk_level"] = event.details.get("risk_level")
                    action_plan["requires_approval"] = event.details.get("requires_approval")
        elif event.event_type == "EXECUTION_COMPLETED":
            if event.details:
                execution_result = event.details.get("execution_result")
        elif event.event_type in ["EXECUTION_FAILED", "GROUNDING_FAILED", "WORKFLOW_FAILED"]:
            if event.details:
                error_message = event.details.get("error") or str(event.details.get("grounding_errors", ""))

    response_data.update({
        "action_plan": action_plan,
        "safety_result": safety_result,
        "execution_result": execution_result,
        "error_message": error_message,
    })

    # 3. Check for pending human approval
    approval = get_pending_approval_by_email_id(db=db, email_id=email_id)
    if approval:
        response_data["approval_id"] = approval.id
        response_data["approval_status"] = approval.status
    else:
        # Check audit events for a resolved approval
        for event in reversed(audit_events):
            if event.event_type in ["APPROVAL_CREATED", "APPROVAL_APPROVED", "APPROVAL_REJECTED"]:
                response_data["approval_id"] = event.approval_id
                if event.event_type == "APPROVAL_APPROVED":
                    response_data["approval_status"] = "APPROVED"
                elif event.event_type == "APPROVAL_REJECTED":
                    response_data["approval_status"] = "REJECTED"
                elif event.event_type == "APPROVAL_CREATED" and response_data.get("approval_status") is None:
                    response_data["approval_status"] = "PENDING"

    return response_data


# ---------------------------------------------------------
# GET EMAIL AUDIT TRAIL
# ---------------------------------------------------------

@router.get(
    "/{email_id}/audit",
    response_model=list[AuditEventResponse],
)
@limiter.limit("60/minute")
def read_email_audit_trail(
    request: Request,
    email_id: int,
    db: Session = Depends(get_db),
):
    """
    Get the chronological audit trail for a single email.
    """

    email = get_email(
        db=db,
        email_id=email_id,
    )

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    return get_email_audit_events(
        db=db,
        email_id=email_id,
    )


# ---------------------------------------------------------
# CREATE EMAIL
# ---------------------------------------------------------

@router.post(
    "",
    response_model=EmailResponse,
)
@limiter.limit("60/minute")
def create_email(
    request: Request,
    email_data: EmailCreate,
    db: Session = Depends(get_db),
):
    """
    Create an email in the database.

    Gmail ingestion uses the dedicated Gmail ingestion
    service. This endpoint is mainly useful for API
    testing and manual email creation.
    """

    email = ingest_email(
        db=db,
        provider_message_id=email_data.provider_message_id,
        thread_id=email_data.thread_id,
        sender=email_data.sender,
        recipients=email_data.recipients,
        subject=email_data.subject,
        body=email_data.body,
        received_at=email_data.received_at,
    )

    return email


# ---------------------------------------------------------
# PROCESS EMAIL
# ---------------------------------------------------------

@router.post(
    "/{email_id}/process",
)
@limiter.limit("20/minute")
def process_email(
    request: Request,
    email_id: int,
    db: Session = Depends(get_db),
):
    """
    Queue an email for background processing.

    FastAPI does not perform the AI processing itself.

    Flow:

        FastAPI
           ↓
        Celery
           ↓
        Redis
           ↓
        Celery Worker
           ↓
        EmailPipeline
    """

    email = get_email(
        db=db,
        email_id=email_id,
    )

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    if email.status != "PENDING":
        raise HTTPException(
            status_code=400,
            detail=(
                f"Email cannot be processed. "
                f"Current status: {email.status}"
            ),
        )

    task = process_email_pipeline.delay(  # type: ignore
        email.id
    )

    return {
        "message": "Email processing queued successfully.",
        "email_id": email.id,
        "task_id": task.id,
        "status": "QUEUED",
    }