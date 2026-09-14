from app.db.database import SessionLocal
from app.integrations.gmail.client import get_gmail_service
from app.models.google_account import GoogleAccount


def main() -> None:
    print("Testing Gmail Archive Integration")
    print("=" * 60)

    db = SessionLocal()

    try:
        account = db.query(GoogleAccount).first()

        if account is None:
            raise RuntimeError("No Google account found.")

        service = get_gmail_service(
            db=db,
            account=account,
        )

        response = (
            service.users()
            .messages()
            .list(
                userId="me",
                q="subject:(Archive Test)",
                maxResults=10,
            )
            .execute()
        )

        messages = response.get("messages", [])

        if not messages:
            print()
            print("No test email found.")
            print()
            print("Create an email with this subject first:")
            print("InboxPilot Archive Test")
            return

        message_id = messages[0]["id"]

        print()
        print("TEST EMAIL FOUND")
        print("-" * 60)
        print(f"Message ID: {message_id}")

        result = service.users().messages().modify(
            userId="me",
            id=message_id,
            body={
                "removeLabelIds": ["INBOX"],
            },
        ).execute()

        print()
        print("ARCHIVE RESULT")
        print("-" * 60)
        print(f"Message ID: {result['id']}")
        print("Email archived successfully.")

        print()
        print("Gmail archive test passed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()