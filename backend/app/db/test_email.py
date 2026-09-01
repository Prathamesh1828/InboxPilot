from app.db.database import SessionLocal
from app.models.email import Email


def test_update_email():
    db = SessionLocal()

    try:
        email = db.query(Email).filter(Email.id == 1).first()

        if email:
            print(f"Current status: {email.status}")

            email.status = "PROCESSING"

            db.commit()
            db.refresh(email)

            print("Email updated successfully!")
            print(f"New status: {email.status}")

        else:
            print("Email not found.")

    finally:
        db.close()


if __name__ == "__main__":
    test_update_email()