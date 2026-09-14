from datetime import datetime, timedelta, timezone

from app.db.database import SessionLocal
from app.integrations.google_calendar.client import (
    create_calendar_event,
    get_calendar_service,
)
from app.models.google_account import GoogleAccount


def main() -> None:
    print("Testing Google Calendar Integration")
    print("=" * 60)

    db = SessionLocal()

    try:
        account = db.query(GoogleAccount).first()

        if account is None:
            raise RuntimeError("No Google account found in database.")

        start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        event_id = create_calendar_event(
            db=db,
            account=account,
            title="InboxPilot Calendar Test",
            start_time=start_time,
            end_time=end_time,
            description="Test event created by InboxPilot.",
        )

        print()
        print("EVENT CREATED")
        print("-" * 60)
        print(f"Event ID: {event_id}")
        print("Title:    InboxPilot Calendar Test")

        # Delete the test event so it does not remain
        # in the user's calendar.
        service = get_calendar_service(
            db=db,
            account=account,
        )

        service.events().delete(
            calendarId="primary",
            eventId=event_id,
        ).execute()

        print()
        print("EVENT CLEANUP")
        print("-" * 60)
        print("Test event deleted successfully.")

        print()
        print("Google Calendar integration test passed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()