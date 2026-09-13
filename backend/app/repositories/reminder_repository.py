from datetime import date

from sqlalchemy.orm import Session

from app.models.reminder import Reminder


def get_reminder_by_email_id(
    db: Session,
    email_id: int,
) -> Reminder | None:
    return (
        db.query(Reminder)
        .filter(Reminder.email_id == email_id)
        .first()
    )


def create_reminder(
    db: Session,
    email_id: int,
    reminder_text: str,
    reminder_date: date | None,
) -> Reminder:
    reminder = Reminder(
        email_id=email_id,
        reminder_text=reminder_text,
        reminder_date=reminder_date,
    )

    db.add(reminder)
    db.commit()
    db.refresh(reminder)

    return reminder