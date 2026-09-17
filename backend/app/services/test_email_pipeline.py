from datetime import datetime, timezone

from app.db.database import SessionLocal
from app.models.email import Email
from app.workers.tasks import process_email_pipeline


def test_email_pipeline():
    print("Testing InboxPilot email pipeline")
    print("=" * 60)

    db = SessionLocal()

    try:
        email = Email(
            provider_message_id=(
                f"pipeline-test-{datetime.now(timezone.utc).timestamp()}"
            ),
            thread_id="pipeline-test-thread",
            sender="test@example.com",
            recipients=["user@example.com"],
            subject="Your electricity bill is due",
            body=(
                "Your electricity bill of INR 2450 "
                "is due on September 20, 2026."
            ),
            received_at=datetime.now(timezone.utc),
            status="PENDING",
        )

        db.add(email)
        db.commit()
        db.refresh(email)

        print(f"Created email ID: {email.id}")
        print(f"Initial status:   {email.status}")
        print()
        print("Sending email to Celery pipeline...")
        print()

        result = process_email_pipeline.delay(email.id)

        print(f"Celery task ID: {result.id}")
        print()
        print("Waiting for background task...")

        task_result = result.get(timeout=60)

        print()
        print("=" * 60)
        print("PIPELINE RESULT")
        print("=" * 60)

        print(task_result)

    finally:
        db.close()


if __name__ == "__main__":
    test_email_pipeline()