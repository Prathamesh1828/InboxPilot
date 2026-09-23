from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.email import Email
from app.schemas.classification import EmailClassification


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
    user_id: str | None = None,
) -> Email:
    email = Email(
        provider_message_id=provider_message_id,
        thread_id=thread_id,
        sender=sender,
        recipients=recipients,
        subject=subject,
        body=body,
        received_at=received_at,
        user_id=user_id,
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
    user_id: str | None = None,
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
        user_id=user_id,
    )

    return email, True


def update_email_status(
    db: Session,
    email: Email,
    status: str,
) -> Email:
    """
    Update the processing status of an email.
    """

    email.status = status

    db.commit()
    db.refresh(email)

    return email


def mark_email_processed(
    db: Session,
    email: Email,
) -> Email:
    """
    Mark an email as completely processed.
    """

    email.status = "COMPLETED"
    email.processed_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(email)

    return email


def update_email_classification(
    db: Session,
    email: Email,
    classification: EmailClassification,
    status: str,
) -> Email:
    """
    Store the LLM classification result for an email.

    The classification contains:
        - category
        - confidence
        - reasoning

    The status is determined by the classification safety gate,
    for example:
        - CLASSIFIED
        - REVIEW
    """

    email.category = classification.category.value
    email.classification_confidence = classification.confidence
    email.classification_reasoning = classification.reasoning
    email.classified_at = datetime.now(timezone.utc)
    email.status = status

    db.commit()
    db.refresh(email)

    return email

def get_pending_emails(
    db: Session,
) -> list[Email]:
    """
    Return all emails that are waiting for classification.
    """

    return (
        db.query(Email)
        .filter(Email.status == "PENDING")
        .order_by(Email.id.asc())
        .all()
    )

def get_emails(
    db: Session,
) -> list[Email]:
    """
    Return all emails ordered from newest to oldest.
    """

    return (
        db.query(Email)
        .order_by(Email.created_at.desc())
        .all()
    )


def get_emails_by_user(
    db: Session,
    user_id: str,
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
) -> tuple[list[Email], int]:
    """
    Return all emails for a specific user, with filtering, sorting, and pagination.
    Returns (items, total_count).
    """
    from sqlalchemy import or_, desc, asc

    query = db.query(Email).filter(Email.user_id == user_id)

    # 1. Search
    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Email.sender.ilike(search_term),
                Email.subject.ilike(search_term),
                Email.body.ilike(search_term),
            )
        )

    # 2. Filters
    if category:
        query = query.filter(Email.category == category)
        
    if status:
        query = query.filter(Email.status == status)

    if confidence_min is not None:
        # Confidence is 0-1 float in DB, we receive 0-100 int
        query = query.filter(Email.classification_confidence >= (confidence_min / 100.0))
        
    if confidence_max is not None:
        query = query.filter(Email.classification_confidence <= (confidence_max / 100.0))

    if date_from:
        try:
            dt_from = datetime.fromisoformat(date_from.replace("Z", "+00:00"))
            query = query.filter(Email.received_at >= dt_from)
        except ValueError:
            pass

    if date_to:
        try:
            dt_to = datetime.fromisoformat(date_to.replace("Z", "+00:00"))
            query = query.filter(Email.received_at <= dt_to)
        except ValueError:
            pass

    # 3. Total Count
    total_count = query.count()

    # 4. Sorting
    # Valid sort columns to prevent injection
    valid_sort_columns = {
        "received_at": Email.received_at,
        "sender": Email.sender,
        "category": Email.category,
        "classification_confidence": Email.classification_confidence,
        "status": Email.status,
    }

    sort_col = valid_sort_columns.get(sort_by, Email.received_at)
    if sort_order.lower() == "asc":
        query = query.order_by(asc(sort_col))
    else:
        query = query.order_by(desc(sort_col))

    # 5. Pagination
    if page < 1:
        page = 1
    if limit < 1 or limit > 100:
        limit = 50

    items = query.offset((page - 1) * limit).limit(limit).all()

    return items, total_count


def get_emails_count_by_user(
    db: Session,
    user_id: str,
) -> int:
    """
    Count emails belonging to a user.
    """
    from sqlalchemy import func
    return db.query(func.count(Email.id)).filter(Email.user_id == user_id).scalar() or 0

def delete_emails_by_user(db: Session, user_id: str) -> int:
    """
    Delete all emails associated with a user.
    Returns the number of deleted records.
    """
    deleted_count = db.query(Email).filter(Email.user_id == user_id).delete()
    db.commit()
    return deleted_count