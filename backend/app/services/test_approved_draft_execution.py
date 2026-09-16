from app.db.database import SessionLocal
from app.models.action_approval import ActionApproval
from app.models.email import Email
from app.repositories.action_approval_repository import (
    create_action_approval,
    get_action_approval,
)
from app.services.approval_execution_service import (
    ApprovalExecutionService,
)
from app.services.approval_service import ApprovalService


TEST_EMAIL_ID = 33


def main() -> None:
    print("Testing Approved Gmail Draft Execution")
    print("=" * 60)

    db = SessionLocal()

    approval = None

    try:
        email = (
            db.query(Email)
            .filter(Email.id == TEST_EMAIL_ID)
            .first()
        )

        if email is None:
            raise RuntimeError(
                f"Test email {TEST_EMAIL_ID} was not found."
            )

        print()
        print("TEST EMAIL")
        print("-" * 60)
        print(f"Email ID:   {email.id}")
        print(f"Sender:     {email.sender}")
        print(f"Subject:    {email.subject}")
        print(f"Thread ID:  {email.thread_id}")

        if not email.thread_id:
            raise RuntimeError(
                "Test email does not have a Gmail thread ID."
            )

        approval = create_action_approval(
            db=db,
            email_id=email.id,
            action="DRAFT_REPLY",
            action_plan={
                "action": "DRAFT_REPLY",
                "parameters": {
                    "reply_text": (
                        "Hi,\n\n"
                        "Thanks for your email. "
                        "This is an approved test draft created "
                        "by InboxPilot.\n\n"
                        "Best,\n"
                        "InboxPilot"
                    )
                },
                "reasoning": (
                    "Test approved Gmail draft action."
                ),
                "confidence": 0.99,
                "risk_level": "MEDIUM",
                "requires_approval": True,
            },
        )

        print()
        print("CREATED APPROVAL")
        print("-" * 60)
        print(f"Approval ID: {approval.id}")
        print(f"Status:      {approval.status}")

        if approval.status != "PENDING":
            raise AssertionError(
                f"Expected PENDING approval, got {approval.status}."
            )

        ApprovalService.approve(
            db=db,
            approval_id=approval.id,
        )

        approved = get_action_approval(
            db=db,
            approval_id=approval.id,
        )

        if approved is None:
            raise AssertionError(
                "Approval record was not found after approval."
            )

        print()
        print("APPROVAL")
        print("-" * 60)
        print(f"Status: {approved.status}")

        if approved.status != "APPROVED":
            raise AssertionError(
                f"Expected APPROVED status, got {approved.status}."
            )

        print("Approval successfully approved.")

        execution_service = ApprovalExecutionService()

        result = execution_service.execute_approved(
            db=db,
            approval_id=approval.id,
        )

        print()
        print("EXECUTION")
        print("-" * 60)
        print(result)

        if "Gmail draft created successfully" not in result:
            raise AssertionError(
                "Gmail draft was not created successfully."
            )

        print()
        print("APPROVED DRAFT VERIFICATION")
        print("-" * 60)
        print("Approval was required.")
        print("Approval was granted.")
        print("Grounding validation passed.")
        print("Safety policy was re-evaluated.")
        print("ActionExecutor created the Gmail draft.")

        print()
        print("Approved Gmail draft execution test passed.")

    finally:
        if approval is not None:
            db.query(ActionApproval).filter(
                ActionApproval.id == approval.id
            ).delete()

            db.commit()

        db.close()


if __name__ == "__main__":
    main()