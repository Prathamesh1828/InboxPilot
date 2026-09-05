from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.email import Email


def get_email_by_id(
    db: Session,
    email_id: int,
) -> Email | None:
    return (
        db.query(Email)
        .filter(Email.id == email_id)
        .first()
    )


def get_email_by_provider_message_id(
    db: Session,
    provider_message_id: str,
) -> Email | None:
    return (
        db.query(Email)
        .filter(
            Email.provider_message_id == provider_message_id
        )
        .first()
    )


def create_email(
    db: Session,
    provider_message_id: str,
    thread_id: str | None,
    sender: str,
    recipients: list[str],
    subject: str | None,
    body: str,
    received_at: datetime,
) -> Email:
    email = Email(
        provider_message_id=provider_message_id,
        thread_id=thread_id,
        sender=sender,
        recipients=recipients,
        subject=subject,
        body=body,
        received_at=received_at,
    )

    db.add(email)
    db.commit()
    db.refresh(email)

    return email


def create_email_if_not_exists(
    db: Session,
    provider_message_id: str,
    thread_id: str | None,
    sender: str,
    recipients: list[str],
    subject: str | None,
    body: str,
    received_at: datetime,
) -> tuple[Email, bool]:
    """
    Create an email if it does not already exist.

    Returns:
        tuple[Email, bool]:
            - Email object
            - True if a new email was created
            - False if the email already existed
    """

    existing_email = get_email_by_provider_message_id(
        db,
        provider_message_id,
    )

    if existing_email:
        return existing_email, False

    email = create_email(
        db=db,
        provider_message_id=provider_message_id,
        thread_id=thread_id,
        sender=sender,
        recipients=recipients,
        subject=subject,
        body=body,
        received_at=received_at,
    )

    return email, True


def update_email_status(
    db: Session,
    email: Email,
    status: str,
) -> Email:
    email.status = status

    db.commit()
    db.refresh(email)

    return email


def mark_email_processed(
    db: Session,
    email: Email,
) -> Email:
    email.status = "COMPLETED"
    email.processed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(email)

    return email