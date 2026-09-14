from app.db.database import SessionLocal
from app.models.email import Email
from app.models.google_account import GoogleAccount
from app.schemas.action_plan import (
    ActionType,
    ArchiveActionPlan,
    ArchiveParameters,
    RiskLevel,
)
from app.services.email_ingestion import ingest_inbox_emails
from app.services.executor import ActionExecutor


TEST_MESSAGE_ID = "1a0a06a3db54178d"


def main() -> None:
    print("Testing Gmail Archive Action Executor")
    print("=" * 60)

    db = SessionLocal()

    try:
        account = db.query(GoogleAccount).first()

        if account is None:
            raise RuntimeError("No Google account found.")

        print()
        print("INGESTING TEST EMAIL")
        print("-" * 60)

        ingestion_result = ingest_inbox_emails(
            db=db,
            account=account,
            max_results=10,
        )

        print(ingestion_result)

        test_email = (
            db.query(Email)
            .filter(
                Email.provider_message_id == TEST_MESSAGE_ID
            )
            .first()
        )

        if test_email is None:
            raise RuntimeError(
                "Archive test email was not found in the database "
                "after ingestion."
            )

        print()
        print("DATABASE EMAIL FOUND")
        print("-" * 60)
        print(f"Database ID: {test_email.id}")
        print(f"Provider Message ID: {test_email.provider_message_id}")
        print(f"Subject: {test_email.subject}")

        plan = ArchiveActionPlan(
            action=ActionType.ARCHIVE,
            parameters=ArchiveParameters(
                reason="InboxPilot archive executor test"
            ),
            reasoning="Testing Gmail archive execution.",
            confidence=0.99,
            risk_level=RiskLevel.LOW,
            requires_approval=False,
        )

        executor = ActionExecutor()

        print()
        print("EXECUTING ARCHIVE ACTION")
        print("-" * 60)

        result = executor.execute(
            plan=plan,
            db=db,
            email_id=test_email.id,
        )

        print()
        print("EXECUTION RESULT")
        print("-" * 60)
        print(result)

        print()
        print("Gmail archive executor test passed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()