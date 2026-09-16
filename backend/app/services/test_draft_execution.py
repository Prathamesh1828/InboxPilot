from app.db.database import SessionLocal
from app.models.email import Email
from app.models.google_account import GoogleAccount
from app.schemas.action_plan import (
    ActionType,
    DraftReplyActionPlan,
    DraftReplyParameters,
    RiskLevel,
)
from app.services.executor import ActionExecutor


TEST_EMAIL_ID = 33


def main() -> None:
    print("Testing Gmail Draft Reply Action Executor")
    print("=" * 60)

    db = SessionLocal()

    try:
        account = db.query(GoogleAccount).first()

        if account is None:
            raise RuntimeError("No Google account found.")

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
        print(f"Database ID: {email.id}")
        print(f"Sender:      {email.sender}")
        print(f"Subject:     {email.subject}")
        print(f"Thread ID:   {email.thread_id}")

        plan = DraftReplyActionPlan(
            action=ActionType.DRAFT_REPLY,
            parameters=DraftReplyParameters(
                reply_text=(
                    "Hi,\n\n"
                    "Thanks for your email. "
                    "This is a test draft created by InboxPilot.\n\n"
                    "Best,\n"
                    "InboxPilot"
                )
            ),
            reasoning="Testing Gmail draft reply execution.",
            confidence=0.99,
            risk_level=RiskLevel.MEDIUM,
            requires_approval=True,
        )

        executor = ActionExecutor()

        print()
        print("EXECUTING DRAFT REPLY")
        print("-" * 60)

        result = executor.execute(
            plan=plan,
            db=db,
            email_id=email.id,
        )

        print()
        print("EXECUTION RESULT")
        print("-" * 60)
        print(result)

        if "Gmail draft created successfully" not in result:
            raise AssertionError(
                "Gmail draft was not created successfully."
            )

        print()
        print("Gmail draft reply executor test passed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()