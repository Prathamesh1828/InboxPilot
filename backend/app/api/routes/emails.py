from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_db
from app.services.email_service import (
    get_email,
    ingest_email,
    start_processing_email,
    complete_email_processing,
)
from app.schemas.email import EmailCreate, EmailResponse

router = APIRouter(
    prefix="/emails",
    tags=["Emails"],
)

@router.get(
    "/{email_id}",
    response_model=EmailResponse,
)

def read_email(
    email_id: int,
    db: Session = Depends(get_db),
):
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

@router.post(
    "",
    response_model=EmailResponse,
)
def create_email(
    email_data: EmailCreate,
    db: Session = Depends(get_db),
):
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

@router.post(
    "/{email_id}/process",
    response_model=EmailResponse,
)
def process_email(
    email_id: int,
    db: Session = Depends(get_db),
):
    email = start_processing_email(
        db=db,
        email_id=email_id,
    )

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    return email

@router.post(
    "/{email_id}/complete",
    response_model=EmailResponse,
)
def complete_email(
    email_id: int,
    db: Session = Depends(get_db),
):
    email = complete_email_processing(
        db=db,
        email_id=email_id,
    )

    if email is None:
        raise HTTPException(
            status_code=404,
            detail="Email not found",
        )

    return email