from app.db.database import SessionLocal
from app.models.google_account import GoogleAccount
from app.integrations.gmail.fetcher import fetch_inbox_messages
from app.integrations.gmail.parser import parse_gmail_message


def main():
    db = SessionLocal()

    try:
        account = (
            db.query(GoogleAccount)
            .filter(
                GoogleAccount.email
                == "test.sample8400@gmail.com"
            )
            .first()
        )

        if not account:
            print("❌ Google account not found.")
            return

        print("Fetching one Gmail message...")
        print()

        messages = fetch_inbox_messages(
            db=db,
            account=account,
            max_results=1,
        )

        if not messages:
            print("❌ No inbox messages found.")
            return

        message = messages[0]

        parsed_email = parse_gmail_message(
            message
        )

        body = parsed_email["body"]

        print("=" * 60)
        print("PARSER TEST RESULT")
        print("=" * 60)

        print(f"Provider ID:    {parsed_email['provider_message_id']}")
        print(f"Subject:        {parsed_email['subject']}")
        print(f"Sender:         {parsed_email['sender']}")
        print(f"Body characters: {len(body)}")

        print()
        print("BODY PREVIEW")
        print("-" * 60)
        print(body[:3000])
        print("-" * 60)

    except Exception as e:
        print("❌ Parser test failed")
        print(f"{type(e).__name__}: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    main()