from app.db.database import SessionLocal
from app.services.email_service import complete_email_processing


def test_complete_email_processing():
    db = SessionLocal()

    try:
        email = complete_email_processing(
            db=db,
            email_id=3,
        )

        if email:
            print("Email completed successfully!")
            print(f"Database ID: {email.id}")
            print(f"Subject: {email.subject}")
            print(f"Status: {email.status}")
            print(f"Processed at: {email.processed_at}")
        else:
            print("Email not found.")

        print()

        missing_email = complete_email_processing(
            db=db,
            email_id=999,
        )

        if missing_email is None:
            print("Missing email test:")
            print("Email ID 999 was not found safely.")

    finally:
        db.close()


if __name__ == "__main__":
    test_complete_email_processing()