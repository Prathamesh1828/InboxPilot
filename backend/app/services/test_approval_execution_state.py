from datetime import datetime, timedelta, timezone

from app.db.database import SessionLocal
from app.integrations.google_calendar.client import get_calendar_service
from app.models.google_account import GoogleAccount
from app.models.email import Email
from app.repositories.action_approval_repository import (
    create_action_approval,
    get_action_approval,
)
from app.repositories.email_repository import get_email_by_id
from app.services.approval_execution_service import ApprovalExecutionService
from app.services.approval_service import ApprovalService


def setup_dummy_email_and_approval(db, account, missing_end_time=False, invalid_start_time=False):
    start_time = datetime.now(timezone.utc) + timedelta(hours=1)
    end_time = start_time + timedelta(hours=1)
    
    start_str = "invalid_start" if invalid_start_time else start_time.isoformat()
    end_str = None if missing_end_time else end_time.isoformat()
    
    body_text = f"Let's schedule a meeting from {start_str}"
    if end_str:
        body_text += f" to {end_str}"
    body_text += " for Temporary approved action test."
    
    dummy_email = Email(
        provider_message_id=f"test_msg_{datetime.now().timestamp()}",
        thread_id="test_thread",
        subject="Test Calendar Approval",
        sender="test@example.com",
        recipients=["test@example.com"],
        body=body_text,
        received_at=datetime.now(timezone.utc)
    )
    db.add(dummy_email)
    db.commit()
    db.refresh(dummy_email)
    
    action_plan = {
        "action": "CREATE_CALENDAR_EVENT",
        "parameters": {
            "title": "InboxPilot Approved Calendar Test",
            "start_time": start_str,
            "end_time": end_str,
            "description": "Temporary approved action test.",
        },
        "reasoning": "Testing approved Calendar execution state.",
        "confidence": 0.99,
        "risk_level": "MEDIUM",
        "requires_approval": True,
    }

    approval = create_action_approval(
        db=db,
        email_id=dummy_email.id,
        action="CREATE_CALENDAR_EVENT",
        action_plan=action_plan,
    )
    
    return dummy_email.id, approval.id

def cleanup(db, email_ids, event_ids, account):
    try:
        service = get_calendar_service(db=db, account=account)
        for eid in event_ids:
            try:
                service.events().delete(calendarId="primary", eventId=eid).execute()
            except Exception:
                pass
                
        for email_id in email_ids:
            from app.models.action_approval import ActionApproval
            approvals = db.query(ActionApproval).filter(ActionApproval.email_id == email_id).all()
            for app in approvals:
                db.delete(app)
            db.commit()
            email = db.query(Email).get(email_id)
            if email:
                db.delete(email)
                db.commit()
    except Exception as e:
        print(f"Cleanup error: {e}")


def main() -> None:
    print("Testing Approval Execution State Scenarios")
    print("=" * 60)

    db = SessionLocal()
    account = db.query(GoogleAccount).first()
    if not account:
        print("No connected Google account found.")
        return
        
    email_ids = []
    event_ids = []

    try:
        # Scenario 1: successful approval -> execution -> EXECUTED + COMPLETED
        print("\nScenario 1: Successful Execution Updates State")
        e1, a1 = setup_dummy_email_and_approval(db, account)
        email_ids.append(e1)
        
        ApprovalService.approve(db=db, approval_id=a1)
        res_1 = ApprovalExecutionService.execute_approved(db=db, approval_id=a1)
        
        # Verify state
        app1 = get_action_approval(db, a1)
        em1 = get_email_by_id(db, e1)
        assert app1.status == "EXECUTED", f"Expected EXECUTED, got {app1.status}"
        assert em1.status == "COMPLETED", f"Expected COMPLETED, got {em1.status}"
        print("Success: State correctly updated to EXECUTED and COMPLETED.")
        
        event_ids.append(res_1.split("Google Event ID: ")[1].rstrip("."))
        
        # Scenario 2: executed approval cannot execute twice
        print("\nScenario 2: Executed approval cannot execute twice")
        try:
            ApprovalService.approve(db=db, approval_id=a1)
            print("FAILED: Expected ValueError on duplicate approve")
        except ValueError as e:
            print(f"Success (Approve blocked): {e}")
            
        try:
            ApprovalExecutionService.execute_approved(db=db, approval_id=a1)
            print("FAILED: Expected ValueError on duplicate execute")
        except ValueError as e:
            print(f"Success (Execute blocked): {e}")
            
        # Scenario 3: execution failure -> no COMPLETED email, safely retryable
        print("\nScenario 3: Execution Failure (Invalid Start) -> Retryable")
        e3, a3 = setup_dummy_email_and_approval(db, account, invalid_start_time=True)
        email_ids.append(e3)
        
        ApprovalService.approve(db=db, approval_id=a3)
        try:
            ApprovalExecutionService.execute_approved(db=db, approval_id=a3)
            print("FAILED: Expected execution to fail due to invalid start time")
        except ValueError as e:
            print(f"Success (Execution failed): {e}")
            
        # Verify state
        app3 = get_action_approval(db, a3)
        em3 = get_email_by_id(db, e3)
        assert app3.status == "PENDING", f"Expected reverted to PENDING, got {app3.status}"
        assert em3.status != "COMPLETED", f"Expected NOT COMPLETED, got {em3.status}"
        print("Success: State correctly reverted to PENDING and email NOT COMPLETED.")
        
        # Retryable check
        try:
            ApprovalService.approve(db=db, approval_id=a3)
            print("Success: Approval could be approved again (Retryable).")
        except ValueError as e:
            print(f"FAILED: Could not re-approve: {e}")
            
        # Scenario 4: rejected approval cannot execute
        print("\nScenario 4: Rejected Approval Cannot Execute")
        e4, a4 = setup_dummy_email_and_approval(db, account)
        email_ids.append(e4)
        
        ApprovalService.reject(db=db, approval_id=a4)
        try:
            ApprovalExecutionService.execute_approved(db=db, approval_id=a4)
            print("FAILED: Expected ValueError on executing rejected approval")
        except ValueError as e:
            print(f"Success: {e}")

        print("\nAll state execution scenarios passed.")
    finally:
        cleanup(db, email_ids, event_ids, account)
        db.close()

if __name__ == "__main__":
    main()
