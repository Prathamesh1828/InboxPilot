from datetime import datetime, timedelta, timezone

from app.db.database import SessionLocal
from app.integrations.google_calendar.client import get_calendar_service
from app.models.google_account import GoogleAccount
from app.models.email import Email
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
    email_id = None

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

        # Create a dummy email so grounding validation passes
        dummy_email = Email(
            provider_message_id="test_msg_id_approved_cal",
            thread_id="test_thread_id_approved_cal",
            subject="Test Calendar Approval",
            sender="test@example.com",
            recipients=["test@example.com"],
            body=f"Let's schedule a meeting from {start_time.isoformat()} to {end_time.isoformat()} for Temporary approved action test.",
            received_at=datetime.now(timezone.utc)
        )
        db.add(dummy_email)
        db.commit()
        db.refresh(dummy_email)
        email_id = dummy_email.id

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
        if email_id:
            from app.models.action_approval import ActionApproval
            approvals = db.query(ActionApproval).filter(ActionApproval.email_id == email_id).all()
            for app in approvals:
                db.delete(app)
            db.commit()
            email = db.query(Email).get(email_id)
            if email:
                db.delete(email)
                db.commit()
        db.close()


if __name__ == "__main__":
    main()