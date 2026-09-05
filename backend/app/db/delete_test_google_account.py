from app.db.database import SessionLocal
from app.models.google_account import GoogleAccount


def main():
    db = SessionLocal()

    try:
        account = (
            db.query(GoogleAccount)
            .filter(GoogleAccount.email == "test_oauth@example.com")
            .first()
        )

        if not account:
            print("No test Google account found.")
            return

        db.delete(account)
        db.commit()

        print("✅ Test Google account deleted.")

    finally:
        db.close()


if __name__ == "__main__":
    main()