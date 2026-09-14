from datetime import datetime, timedelta, timezone

from app.db.database import SessionLocal
from app.models.google_account import GoogleAccount
from app.schemas.action_plan import (
    CalendarActionPlan,
    CalendarEventParameters,
    ActionType,
    RiskLevel,
)
from app.services.executor import ActionExecutor


def main() -> None:
    print("Testing Calendar Action Executor")
    print("=" * 60)

    db = SessionLocal()
    event_id = None

    try:
        account = db.query(GoogleAccount).first()

        if account is None:
            raise RuntimeError("No Google account found.")

        start_time = datetime.now(timezone.utc) + timedelta(hours=1)
        end_time = start_time + timedelta(hours=1)

        plan = CalendarActionPlan(
            action=ActionType.CREATE_CALENDAR_EVENT,
            parameters=CalendarEventParameters(
                title="InboxPilot Executor Test",
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                description="Temporary test event.",
            ),
            reasoning="Testing Calendar execution.",
            confidence=0.99,
            risk_level=RiskLevel.MEDIUM,
            requires_approval=True,
        )

        executor = ActionExecutor()

        result = executor.execute(
            plan=plan,
            db=db,
        )

        print()
        print("EXECUTION RESULT")
        print("-" * 60)
        print(result)

        # Extract event ID from the result.
        event_id = result.split("Google Event ID: ")[1].rstrip(".")

        print()
        print("Calendar executor test passed.")

        # Delete the temporary event.
        from app.integrations.google_calendar.client import (
            get_calendar_service,
        )

        service = get_calendar_service(
            db=db,
            account=account,
        )

        service.events().delete(
            calendarId="primary",
            eventId=event_id,
        ).execute()

        print()
        print("CLEANUP")
        print("-" * 60)
        print("Temporary calendar event deleted.")

    finally:
        db.close()


if __name__ == "__main__":
    main()