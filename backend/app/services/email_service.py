from datetime import datetime

from sqlalchemy.orm import Session

from app.models.email import Email
from app.repositories.email_repository import (
    create_email,
    get_email_by_id,
    get_email_by_provider_message_id,
    mark_email_processed,
    update_email_status,
)

def ingest_email(
    db: Session,
    provider_message_id: str,
    thread_id: str | None,
    sender: str,
    recipients: list[str],
    subject: str | None,
    body: str,
    received_at: datetime,
) -> Email:
    existing_email = get_email_by_provider_message_id(
        db=db,
        provider_message_id=provider_message_id,
    )

    if existing_email:
        return existing_email

    return create_email(
        db=db,
        provider_message_id=provider_message_id,
        thread_id=thread_id,
        sender=sender,
        recipients=recipients,
        subject=subject,
        body=body,
        received_at=received_at,
    )

def start_processing_email(
    db: Session,
    email_id: int,
) -> Email | None:
    email = get_email_by_id(
        db=db,
        email_id=email_id,
    )

    if email is None:
        return None

    return update_email_status(
        db=db,
        email=email,
        status="PROCESSING",
    )

def complete_email_processing(
    db: Session,
    email_id: int,
) -> Email | None:
    email = get_email_by_id(
        db=db,
        email_id=email_id,
    )

    if email is None:
        return None

    return mark_email_processed(
        db=db,
        email=email,
    )