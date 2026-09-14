from datetime import datetime, timedelta, timezone

from app.db.database import SessionLocal
from app.integrations.google_calendar.client import get_calendar_service
from app.models.google_account import GoogleAccount
from app.repositories.action_approval_repository import (
    create_action_approval,
)
from app.services.approval_execution_service import (
    ApprovalExecutionService,
)
from app.services.approval_service import ApprovalService


def main() -> None:
    print("Testing Approved Calendar Execution")
    print("=" * 60)

    db = SessionLocal()

    event_id = None

    try:
        account = db.query(GoogleAccount).first()

        if account is None:
            raise RuntimeError(
                "No connected Google account found."
            )

        start_time = (
            datetime.now(timezone.utc)
            + timedelta(hours=1)
        )

        end_time = start_time + timedelta(hours=1)

        action_plan = {
            "action": "CREATE_CALENDAR_EVENT",
            "parameters": {
                "title": "InboxPilot Approved Calendar Test",
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "description": "Temporary approved action test.",
            },
            "reasoning": "Testing approved Calendar execution.",
            "confidence": 0.99,
            "risk_level": "MEDIUM",
            "requires_approval": True,
        }

        # Use an existing email only for the approval record.
        # ApprovalExecutionService will retrieve it.
        email_id = 2

        approval = create_action_approval(
            db=db,
            email_id=email_id,
            action="CREATE_CALENDAR_EVENT",
            action_plan=action_plan,
        )

        print()
        print("APPROVAL CREATED")
        print("-" * 60)
        print(f"Approval ID: {approval.id}")
        print(f"Status:      {approval.status}")

        ApprovalService.approve(
            db=db,
            approval_id=approval.id,
        )

        print()
        print("APPROVAL")
        print("-" * 60)
        print("Action approved successfully.")

        result = ApprovalExecutionService.execute_approved(
            db=db,
            approval_id=approval.id,
        )

        print()
        print("EXECUTION RESULT")
        print("-" * 60)
        print(result)

        event_id = result.split(
            "Google Event ID: "
        )[1].rstrip(".")

        print()
        print("Approved Calendar execution test passed.")

        # Clean up the temporary Calendar event.
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
        print("Temporary Calendar event deleted.")

    finally:
        db.close()


if __name__ == "__main__":
    main()