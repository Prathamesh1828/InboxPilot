from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.email import Email
from app.schemas.classification import EmailClassification
from app.security.encryption import (
    decrypt_email_field,
    decrypt_email_recipients,
    encrypt_email_field,
    encrypt_email_recipients,
    is_encrypted,
)



def decrypt_email(email: Email | None) -> Email | None:
    """
    Decrypt all encrypted fields on an Email object IN PLACE and return it.
    Safe to call on plaintext rows (fields without the v1: prefix pass through unchanged).
    Returns None if email is None.
    """
    if email is None:
        return None
    try:
        email.sender = decrypt_email_field(email.sender) or email.sender
        email.subject = decrypt_email_field(email.subject)
        email.body = decrypt_email_field(email.body) or email.body
        # recipients may be stored as encrypted JSON string or as a real list
        if isinstance(email.recipients, str):
            email.recipients = decrypt_email_recipients(email.recipients)
        elif isinstance(email.recipients, list) and email.recipients:
            # check if it looks like an encrypted token (shouldn't be, but guard)
            first = email.recipients[0] if email.recipients else ""
            if isinstance(first, str) and first.startswith("v1:"):
                email.recipients = decrypt_email_recipients(first)
    except Exception as exc:
        import logging as _logging
        _logging.getLogger(__name__).error(
            "Failed to decrypt email id=%s: %s", getattr(email, "id", "?"), type(exc).__name__
        )
        raise ValueError("Failed to decrypt email fields.") from exc
    return email


def get_email_by_id(
    db: Session,
    email_id: int,
) -> Email | None:
    row = (
        db.query(Email)
        .filter(Email.id == email_id)
        .first()
    )
    return decrypt_email(row)


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
        sender=encrypt_email_field(sender) or sender,
        recipients=encrypt_email_recipients(recipients),   # stored as encrypted JSON string
        subject=encrypt_email_field(subject),
        body=encrypt_email_field(body) or body,
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
    rows = (
        db.query(Email)
        .filter(Email.status == "PENDING")
        .order_by(Email.id.asc())
        .all()
    )
    return [e for e in (decrypt_email(r) for r in rows) if e is not None]

def get_emails(
    db: Session,
) -> list[Email]:
    """
    Return all emails ordered from newest to oldest.
    """
    rows = (
        db.query(Email)
        .order_by(Email.created_at.desc())
        .all()
    )
    return [e for e in (decrypt_email(r) for r in rows) if e is not None]


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

    # NOTE: Full-text search on encrypted fields is not possible at the DB layer.
    # When encryption is active, search is skipped to avoid false negatives.
    from app.security.encryption import _AESGCM
    # 1. Search — only possible if email fields are NOT encrypted
    if search and _AESGCM is None:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                Email.sender.ilike(search_term),
                Email.subject.ilike(search_term),
                Email.body.ilike(search_term),
            )
        )
    elif search:
        # When encrypted, we skip DB-level search but will apply post-decryption filter below
        pass

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

    items_raw = query.offset((page - 1) * limit).limit(limit).all()

    # Decrypt all items
    items = [e for e in (decrypt_email(r) for r in items_raw) if e is not None]

    # Post-decryption search filter (only when encryption is active and search was requested)
    from app.security.encryption import _AESGCM
    if search and _AESGCM is not None:
        sl = search.lower()
        items = [
            e for e in items
            if sl in (e.sender or "").lower()
            or sl in (e.subject or "").lower()
            or sl in (e.body or "").lower()
        ]

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

def delete_old_emails(db: Session, days_old: int = 7) -> int:
    """
    Delete emails that are older than X days to save database storage.
    Since foreign keys do not have CASCADE enabled at the DB level for safety,
    we must manually delete child records first (audit_events, action_approvals).
    """
    from datetime import timedelta
    from app.models.action_approval import ActionApproval
    from app.models.audit_event import AuditEvent

    cutoff_date = datetime.now(timezone.utc) - timedelta(days=days_old)

    # 1. Find the IDs of the old emails
    old_email_ids = [
        row[0] for row in 
        db.query(Email.id).filter(Email.created_at < cutoff_date).all()
    ]

    if not old_email_ids:
        return 0

    # 2. Delete Audit Events linked to these emails
    db.query(AuditEvent).filter(AuditEvent.email_id.in_(old_email_ids)).delete(synchronize_session=False)

    # 3. Delete Action Approvals linked to these emails
    db.query(ActionApproval).filter(ActionApproval.email_id.in_(old_email_ids)).delete(synchronize_session=False)

    # 4. Delete the Emails
    deleted_emails = db.query(Email).filter(Email.id.in_(old_email_ids)).delete(synchronize_session=False)

    db.commit()
    return deleted_emails