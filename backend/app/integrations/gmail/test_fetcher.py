from typing import Any

from app.db.database import SessionLocal
from app.integrations.gmail.fetcher import fetch_inbox_messages
from app.repositories.google_account_repository import (
    get_google_account_by_email,
)


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

        messages: list[dict[str, Any]] = fetch_inbox_messages(
            db=db,
            account=account,
            max_results=10,
        )

        print(f"✅ Fetched {len(messages)} Inbox message(s)")

        if not messages:
            print("ℹ️ No messages found in the Inbox.")
            return

        print("\n--- First message ---")

        message = messages[0]

        print(f"Message ID: {message.get('id')}")
        print(f"Thread ID: {message.get('threadId')}")
        print(f"Internal date: {message.get('internalDate')}")
        print(f"Snippet: {message.get('snippet')}")

        payload = message.get("payload", {})
        headers = payload.get("headers", [])

        print("\nHeaders:")

        for header in headers:
            name = header.get("name")
            value = header.get("value")

            if name in {"From", "To", "Subject", "Date"}:
                print(f"{name}: {value}")

    except Exception as e:
        print("❌ Gmail fetcher test failed")
        print(f"{type(e).__name__}: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    main()