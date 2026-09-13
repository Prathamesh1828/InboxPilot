from datetime import date

import app.models

from app.db.database import SessionLocal
from app.repositories.reminder_repository import (
    create_reminder,
    get_reminder_by_email_id,
)


def main() -> None:
    print("Testing Reminder Repository")
    print("=" * 60)

    db = SessionLocal()

    try:
        reminder = create_reminder(
            db=db,
            email_id=1,
            reminder_text="Pay electricity bill",
            reminder_date=date(2026, 9, 20),
        )

        print()
        print("REMINDER CREATED")
        print("-" * 60)
        print(f"ID:              {reminder.id}")
        print(f"Email ID:        {reminder.email_id}")
        print(f"Reminder Text:   {reminder.reminder_text}")
        print(f"Reminder Date:   {reminder.reminder_date}")

        existing_reminder = get_reminder_by_email_id(
            db=db,
            email_id=1,
        )

        print()
        print("REMINDER LOOKUP")
        print("-" * 60)

        if existing_reminder is not None:
            print(
                f"Found reminder ID: "
                f"{existing_reminder.id}"
            )
            print(
                f"Reminder Text: "
                f"{existing_reminder.reminder_text}"
            )
            print(
                f"Reminder Date: "
                f"{existing_reminder.reminder_date}"
            )
        else:
            print("No reminder found.")

    finally:
        db.close()


if __name__ == "__main__":
    main()