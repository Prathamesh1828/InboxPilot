from datetime import datetime, timezone

from app.db.database import SessionLocal
from app.models.email import Email
from app.repositories.action_approval_repository import (
    create_action_approval,
)
from app.services.approval_service import ApprovalService


def main() -> None:
    print("Testing Approval Service")
    print("=" * 60)

    db = SessionLocal()
    test_email = None

    try:
        # Create a dedicated test email
        test_email = Email(
            provider_message_id="test-approval-service-email",
            thread_id="test-approval-service-thread",
            sender="test@example.com",
            subject="Test Approval",
            recipients=["test@example.com"],
            body="Test body",
            received_at=datetime.now(timezone.utc),
            status="CLASSIFIED",
            category="OTHER",
            classification_confidence=0.99,
            classification_reasoning="Test email",
        )

        db.add(test_email)
        db.commit()
        db.refresh(test_email)

        # Create an approval record
        approval = create_action_approval(
            db=db,
            email_id=test_email.id,
            action="DRAFT_REPLY",
            action_plan={
                "action": "DRAFT_REPLY",
                "parameters": {"reply_text": "Rejecting this."},
                "reasoning": "Testing rejection.",
                "confidence": 0.99,
                "risk_level": "LOW",
                "requires_approval": True,
            },
        )

        service = ApprovalService()

        result = service.reject(
            db=db,
            approval_id=approval.id,
        )

        print()
        print("REJECT RESULT")
        print("-" * 60)
        print(result)

    finally:
        if test_email is not None:
            from app.models.action_approval import ActionApproval

            db.query(ActionApproval).filter(
                ActionApproval.email_id == test_email.id
            ).delete()

            db.delete(test_email)
            db.commit()

        db.close()


if __name__ == "__main__":
    main()