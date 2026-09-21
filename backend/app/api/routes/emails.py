from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_api_key
from app.core.limiter import limiter
from app.repositories.email_repository import get_emails
from app.schemas.email import EmailCreate, EmailResponse
from app.services.email_service import (
    get_email,
    ingest_email,
)
from app.repositories.audit_repository import get_email_audit_events
from app.schemas.audit import AuditEventResponse
from app.workers.tasks import process_email_pipeline


router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
    dependencies=[Depends(get_api_key)],
)


# ---------------------------------------------------------
# GET ALL EMAILS
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[EmailResponse],
)
@limiter.limit("60/minute")
def read_emails(
    request: Request,
    db: Session = Depends(get_db),
):
    """
    Get all emails ordered from newest to oldest.
    """

    return get_emails(db=db)


# ---------------------------------------------------------
# GET SINGLE EMAIL
# ---------------------------------------------------------

@router.get(
    "/{email_id}",
    response_model=EmailResponse,
)
@limiter.limit("60/minute")
def read_email(
    request: Request,
    email_id: int,
    db: Session = Depends(get_db),
):
    """
    Get a single email by its database ID.
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

    return email


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

    task = process_email_pipeline.delay(
        email.id
    )

    return {
        "message": "Email processing queued successfully.",
        "email_id": email.id,
        "task_id": task.id,
        "status": "QUEUED",
    }