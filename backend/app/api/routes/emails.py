from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.repositories.email_repository import get_emails
from app.schemas.email import EmailCreate, EmailResponse
from app.services.email_service import (
    get_email,
    ingest_email,
)
from app.workers.tasks import process_email_pipeline


router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
)


# ---------------------------------------------------------
# GET ALL EMAILS
# ---------------------------------------------------------

@router.get(
    "",
    response_model=list[EmailResponse],
)
def read_emails(
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
def read_email(
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
# CREATE EMAIL
# ---------------------------------------------------------

@router.post(
    "",
    response_model=EmailResponse,
)
def create_email(
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
def process_email(
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