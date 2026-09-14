from datetime import datetime, timezone

from app.db.database import SessionLocal
from app.models.email import Email
from app.repositories.action_approval_repository import (
    create_action_approval,
)
from app.services.approval_execution_service import (
    ApprovalExecutionService,
)
from app.services.approval_service import ApprovalService


def main() -> None:
    print("Testing Approved Action Execution")
    print("=" * 60)

    db = SessionLocal()

    test_email = None

    try:
        # Create a dedicated test email.
        test_email = Email(
            provider_message_id="approval-test-email",
            thread_id="approval-test-thread",
            sender="electricity@example.com",
            subject="Electricity Bill",
            recipients=["test@example.com"],
            body=(
                "Your electricity bill is ₹2450. "
                "Payment is due on September 20, 2026."
            ),
            received_at=datetime.now(timezone.utc),
            status="CLASSIFIED",
            category="BILL",
            classification_confidence=0.99,
            classification_reasoning=(
                "Test email containing bill information."
            ),
        )

        db.add(test_email)
        db.commit()
        db.refresh(test_email)

        print()
        print("TEST EMAIL")
        print("-" * 60)
        print(f"Email ID: {test_email.id}")

        # Create approval using parameters grounded in
        # the test email.
        approval = create_action_approval(
            db=db,
            email_id=test_email.id,
            action="LOG_BILL",
            action_plan={
                "action": "LOG_BILL",
                "parameters": {
                    "amount": 2450.0,
                    "currency": "INR",
                    "vendor": "Electricity",
                    "due_date": "2026-09-20",
                },
                "reasoning": "Test approved bill action.",
                "confidence": 0.99,
                "risk_level": "LOW",
                "requires_approval": False,
            },
        )

        print()
        print("CREATED APPROVAL")
        print("-" * 60)
        print(f"Approval ID: {approval.id}")
        print(f"Status:      {approval.status}")

        # Approve the action.
        ApprovalService.approve(
            db=db,
            approval_id=approval.id,
        )

        print()
        print("APPROVAL")
        print("-" * 60)
        print("Approval successfully approved.")

        # Execute the approved action.
        execution_service = ApprovalExecutionService()

        result = execution_service.execute_approved(
            db=db,
            approval_id=approval.id,
        )

        print()
        print("EXECUTION")
        print("-" * 60)
        print(result)

        print()
        print("Approved execution test passed.")

    finally:
        # Remove test data created by this test.
        if test_email is not None:
            from app.models.bill import Bill
            from app.models.action_approval import ActionApproval

            db.query(Bill).filter(
                Bill.email_id == test_email.id
            ).delete()

            db.query(ActionApproval).filter(
                ActionApproval.email_id == test_email.id
            ).delete()

            db.delete(test_email)
            db.commit()

        db.close()


if __name__ == "__main__":
    main()