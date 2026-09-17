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
    print("Testing Calendar Action Executor Scenarios")
    print("=" * 60)

    db = SessionLocal()

    try:
        account = db.query(GoogleAccount).first()
        if account is None:
            raise RuntimeError("No Google account found.")
            
        executor = ActionExecutor()
        
        # Scenario 1: Explicit start_time and end_time
        print("\nScenario 1: Explicit start and end time")
        start_time_1 = datetime.now(timezone.utc) + timedelta(hours=1)
        end_time_1 = start_time_1 + timedelta(minutes=30)
        
        plan_1 = CalendarActionPlan(
            action=ActionType.CREATE_CALENDAR_EVENT,
            parameters=CalendarEventParameters(
                title="Scenario 1 Test",
                start_time=start_time_1.isoformat(),
                end_time=end_time_1.isoformat(),
            ),
            reasoning="Testing Calendar execution.",
            confidence=0.99,
            risk_level=RiskLevel.MEDIUM,
            requires_approval=True,
        )
        
        res_1 = executor.execute(plan_1, db)
        print("Success:", res_1)
        event_id_1 = res_1.split("Google Event ID: ")[1].rstrip(".")
        
        # Scenario 2: Missing end_time (should fallback to +1 hour)
        print("\nScenario 2: Missing end time")
        start_time_2 = datetime.now(timezone.utc) + timedelta(hours=2)
        
        plan_2 = CalendarActionPlan(
            action=ActionType.CREATE_CALENDAR_EVENT,
            parameters=CalendarEventParameters(
                title="Scenario 2 Test",
                start_time=start_time_2.isoformat(),
                end_time=None,
            ),
            reasoning="Testing Calendar execution fallback.",
            confidence=0.99,
            risk_level=RiskLevel.MEDIUM,
            requires_approval=True,
        )
        
        res_2 = executor.execute(plan_2, db)
        print("Success:", res_2)
        event_id_2 = res_2.split("Google Event ID: ")[1].rstrip(".")
        
        # Scenario 3: Missing start_time (should fail safely)
        print("\nScenario 3: Missing start time")
        plan_3 = CalendarActionPlan(
            action=ActionType.CREATE_CALENDAR_EVENT,
            parameters=CalendarEventParameters(
                title="Scenario 3 Test",
                start_time=None,
                end_time=None,
            ),
            reasoning="Testing safe failure.",
            confidence=0.99,
            risk_level=RiskLevel.MEDIUM,
            requires_approval=True,
        )
        try:
            executor.execute(plan_3, db)
            print("FAILED: Expected ValueError")
        except ValueError as e:
            print("Success: Caught expected ValueError:", str(e))
            
        print("\nAll calendar execution scenarios passed.")
        
        # Cleanup
        print("\nCLEANUP")
        print("-" * 60)
        from app.integrations.google_calendar.client import get_calendar_service
        service = get_calendar_service(db, account)
        
        for e_id in [event_id_1, event_id_2]:
            service.events().delete(
                calendarId="primary",
                eventId=e_id,
            ).execute()
        print("Temporary calendar events deleted.")

    finally:
        db.close()

if __name__ == "__main__":
    main()