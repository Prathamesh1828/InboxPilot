from app.db.database import SessionLocal
from app.repositories.email_repository import (
    get_email_by_id,
    mark_email_processed,
)


def test_mark_email_processed():
    db = SessionLocal()

    try:
        email = get_email_by_id(
            db=db,
            email_id=2,
        )

        if email:
            print(f"Current status: {email.status}")
            print(f"Current processed_at: {email.processed_at}")

            updated_email = mark_email_processed(
                db=db,
                email=email,
            )

            print("Email marked as processed!")
            print(f"New status: {updated_email.status}")
            print(f"Processed at: {updated_email.processed_at}")

        else:
            print("Email not found.")

    finally:
        db.close()


if __name__ == "__main__":
    test_mark_email_processed()