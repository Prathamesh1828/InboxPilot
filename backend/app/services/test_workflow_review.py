from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.models.email import Email
from app.services.workflow_service import WorkflowService


def test_review_email_blocked():
    print("Testing REVIEW email workflow protection")
    print("=" * 60)

    db: Session = SessionLocal()

    try:
        email = (
            db.query(Email)
            .filter(Email.status == "CLASSIFIED")
            .order_by(Email.id.desc())
            .first()
        )

        if email is None:
            raise RuntimeError("No CLASSIFIED email found.")

        original_status = email.status

        print(f"Email ID:       {email.id}")
        print(f"Original status: {original_status}")

        # Temporarily move the email into REVIEW.
        email.status = "REVIEW"
        db.commit()
        db.refresh(email)

        print(f"Test status:     {email.status}")
        print()
        print("Attempting to send REVIEW email into workflow...")

        service = WorkflowService()

        try:
            service.process_email(
                db=db,
                email_id=email.id,
            )

            raise AssertionError(
                "REVIEW email was incorrectly allowed into the workflow."
            )

        except ValueError as exc:
            print()
            print("Expected error received:")
            print(exc)
            print()
            print("✅ REVIEW email was correctly blocked.")

        # Restore original status.
        email.status = original_status
        db.commit()

        print()
        print("=" * 60)
        print("✅ REVIEW protection test passed")

    finally:
        db.close()


if __name__ == "__main__":
    test_review_email_blocked()