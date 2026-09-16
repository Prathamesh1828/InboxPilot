from app.db.database import SessionLocal
from app.integrations.gmail.client import create_gmail_draft
from app.models.google_account import GoogleAccount


def main() -> None:
    print("Testing Gmail Draft Integration")
    print("=" * 60)

    db = SessionLocal()

    try:
        account = db.query(GoogleAccount).first()

        if account is None:
            raise RuntimeError("No Google account found.")

        draft_id = create_gmail_draft(
            db=db,
            account=account,
            to=str(account.email),
            subject="InboxPilot Draft Integration Test",
            body=(
                "This is a test draft created by InboxPilot "
                "through the Gmail API."
            ),
        )

        print()
        print("DRAFT CREATED")
        print("-" * 60)
        print(f"Draft ID: {draft_id}")

        print()
        print("Gmail draft integration test passed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()