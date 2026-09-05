from typing import Any

from app.db.database import SessionLocal
from app.integrations.gmail.fetcher import fetch_inbox_messages
from app.integrations.gmail.parser import parse_gmail_message
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

        messages: list[dict[str, Any]] = fetch_inbox_messages(
            db=db,
            account=account,
            max_results=10,
        )

        print(f"✅ Fetched {len(messages)} Inbox message(s)")

        if not messages:
            print("ℹ️ No Inbox messages found.")
            return

        print("\n========== PARSED EMAILS ==========\n")

        for index, message in enumerate(messages, start=1):
            try:
                parsed = parse_gmail_message(message)

                print(f"--- Email {index} ---")
                print(
                    f"Message ID: {parsed['provider_message_id']}"
                )
                print(
                    f"Thread ID: {parsed['thread_id']}"
                )
                print(
                    f"From: {parsed['sender']}"
                )
                print(
                    f"To: {parsed['recipients']}"
                )
                print(
                    f"Subject: {parsed['subject']}"
                )
                print(
                    f"Received: {parsed['received_at']}"
                )

                body = parsed["body"]

                print(
                    f"Body length: {len(body)} characters"
                )

                if body:
                    print("Body preview:")
                    print(body[:500])
                else:
                    print("Body: [empty]")

                print()

            except Exception as e:
                print(
                    f"❌ Failed to parse email {index}"
                )
                print(
                    f"{type(e).__name__}: {e}"
                )
                print()

        print("====================================")
        print("✅ Parser test completed")

    except Exception as e:
        print("❌ Parser test failed")
        print(f"{type(e).__name__}: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    main()