from typing import Any

from app.db.database import SessionLocal
from app.repositories.google_account_repository import (
    get_google_account_by_email,
)
from app.integrations.gmail.client import get_gmail_service


def main():
    db = SessionLocal()

    try:
        # Get the Google account saved during OAuth
        account = get_google_account_by_email(
            db,
            "test.sample8400@gmail.com",
        )

        if not account:
            print("❌ Google account not found in database.")
            return

        print("✅ Google account found")
        print(f"Email: {account.email}")
        print(f"Has access token: {bool(account.access_token)}")
        print(f"Has refresh token: {bool(account.refresh_token)}")
        print(f"Token expiry: {account.token_expiry}")

        # Build authenticated Gmail API client.
        # Google API services are dynamically generated,
        # so Pylance cannot infer methods such as .users().
        service: Any = get_gmail_service(
            db=db,
            account=account,
        )

        print("✅ Gmail API client created successfully")

        # Make a harmless Gmail API request
        profile = (
            service.users()
            .getProfile(
                userId="me",
            )
            .execute()
        )

        print("✅ Gmail API request successful")
        print(f"Gmail address: {profile.get('emailAddress')}")
        print(f"Messages total: {profile.get('messagesTotal')}")
        print(f"Threads total: {profile.get('threadsTotal')}")

    except Exception as e:
        print("❌ Gmail client test failed")
        print(f"{type(e).__name__}: {e}")

    finally:
        db.close()


if __name__ == "__main__":
    main()