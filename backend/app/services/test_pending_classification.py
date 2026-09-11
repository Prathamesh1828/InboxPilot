from app.db.database import SessionLocal
from app.services.classification_service import ClassificationService


def main() -> None:
    print("Testing pending email classification")
    print("=" * 60)

    db = SessionLocal()

    try:
        service = ClassificationService()

        print("Starting classification of pending emails...")
        print()

        results = service.classify_pending_emails(
            db=db,
        )

        print()
        print("=" * 60)
        print("CLASSIFICATION RESULTS")
        print("=" * 60)

        for email in results:
            print()
            print(f"Email ID:      {email.id}")
            print(f"Subject:       {email.subject}")
            print(f"Category:      {email.category}")
            print(
                f"Confidence:    "
                f"{email.classification_confidence}"
            )
            print(f"Status:        {email.status}")
            print(
                f"Reasoning:     "
                f"{email.classification_reasoning}"
            )

        print()
        print("=" * 60)
        print(f"Processed: {len(results)} email(s)")

    except Exception as exc:
        db.rollback()

        print("❌ Batch classification failed")
        print(f"Error type: {type(exc).__name__}")
        print(f"Error: {exc}")

    finally:
        db.close()


if __name__ == "__main__":
    main()