from app.db.database import SessionLocal
from app.repositories.google_account_repository import (
    get_google_account_by_email,
)
from app.services.email_ingestion import ingest_inbox_emails


def main():
    db = SessionLocal()

    try:
        account = get_google_account_by_email(
            db,
            "test.sample8400@gmail.com",
        )

        if not account:
            print("❌ Google account not found in database.")
            return

        print("✅ Google account found")
        print(f"Email: {account.email}")
        print("\nStarting Inbox ingestion...\n")

        result = ingest_inbox_emails(
            db=db,
            account=account,
            max_results=10,
        )

        print("\n========== INGESTION RESULT ==========")
        print(f"Fetched:  {result['fetched']}")
        print(f"Inserted: {result['inserted']}")
        print(f"Skipped:  {result['skipped']}")
        print(f"Failed:   {result['failed']}")
        print("======================================")

    except Exception as e:
        print("❌ Email ingestion test failed")
        print(f"{type(e).__name__}: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    main()