from datetime import datetime, timezone

from app.db.database import SessionLocal
from app.models.email import Email
from app.services.classification_service import ClassificationService


def main() -> None:
    print("Testing InboxPilot classification service")
    print("=" * 60)

    db = SessionLocal()

    try:
        # --------------------------------------------------------
        # 1. Create a test email in the database
        # --------------------------------------------------------

        test_email = Email(
            provider_message_id="classification-service-test-001",
            thread_id="test-thread-001",
            sender="netflix@example.com",
            recipients=["user@example.com"],
            subject="Your Netflix payment is due",
            body=(
                "Your Netflix subscription payment of $15.99 "
                "is due on September 15, 2026. "
                "Please make sure your payment method is up to date."
            ),
            received_at=datetime.now(timezone.utc),
            status="PENDING",
        )

        db.add(test_email)
        db.commit()
        db.refresh(test_email)

        print(f"Test email created with ID: {test_email.id}")
        print(f"Status before classification: {test_email.status}")

        # --------------------------------------------------------
        # 2. Run classification service
        # --------------------------------------------------------

        service = ClassificationService()

        print("\nSending email to classification service...")
        print("Groq → Gemini fallback → Confidence Gate")
        print()

        result = service.classify_email(
            db=db,
            email=test_email,
        )

        # --------------------------------------------------------
        # 3. Display result
        # --------------------------------------------------------

        print("✅ Classification completed")
        print("-" * 60)

        print(f"Email ID:       {result.id}")
        print(f"Category:       {result.category}")
        print(
            f"Confidence:     {result.classification_confidence}"
        )
        print(
            f"Status:         {result.status}"
        )
        print(
            f"Reasoning:      {result.classification_reasoning}"
        )
        print(
            f"Classified at:  {result.classified_at}"
        )

        print("-" * 60)

        if result.category == "BILL":
            print("✅ Category is correct")
        else:
            print(
                f"⚠️ Expected BILL, got {result.category}"
            )

    except Exception as exc:
        db.rollback()

        print("❌ Classification service test failed")
        print("-" * 60)
        print(f"Error type: {type(exc).__name__}")
        print(f"Error: {exc}")

    finally:
        db.close()


if __name__ == "__main__":
    main()