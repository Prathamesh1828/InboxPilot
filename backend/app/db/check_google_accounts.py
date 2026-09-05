from app.db.database import SessionLocal
from app.models.google_account import GoogleAccount


def main():
    db = SessionLocal()

    try:
        accounts = db.query(GoogleAccount).all()

        if not accounts:
            print("❌ No Google accounts found in database.")
            return

        print(f"✅ Found {len(accounts)} Google account(s):")

        for account in accounts:
            print("--------------------------------")
            print(f"ID: {account.id}")
            print(f"Email: {account.email}")
            print(f"Google User ID: {account.google_user_id}")
            print(f"Has access token: {bool(account.access_token)}")
            print(f"Has refresh token: {bool(account.refresh_token)}")
            print(f"Token expiry: {account.token_expiry}")

    finally:
        db.close()


if __name__ == "__main__":
    main()