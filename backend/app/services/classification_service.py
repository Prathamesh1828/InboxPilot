from sqlalchemy.orm import Session

from app.models.email import Email
from app.repositories.email_repository import (
    get_pending_emails,
    update_email_classification,
)
from app.services.classification_gate import evaluate_classification
from app.services.classifier import EmailClassifier


class ClassificationService:
    """
    Coordinates the email classification workflow.

    Flow:

        PENDING email
            ↓
        EmailClassifier
            ↓
        Groq → Gemini fallback
            ↓
        Confidence Gate
            ↓
        CLASSIFIED / REVIEW
            ↓
        PostgreSQL
    """

    def __init__(self) -> None:
        self.classifier = EmailClassifier()

    def classify_email(
        self,
        db: Session,
        email: Email,
    ) -> Email:
        """
        Classify a single email and persist the result.
        """

        classification = self.classifier.classify(
            sender=email.sender,
            recipients=email.recipients,
            subject=email.subject or "",
            body=email.body,
        )

        status = evaluate_classification(
            classification
        )

        return update_email_classification(
            db=db,
            email=email,
            classification=classification,
            status=status,
        )

    def classify_pending_emails(
        self,
        db: Session,
    ) -> list[Email]:
        """
        Classify all currently pending emails.

        Only emails with PENDING status are processed.
        """

        pending_emails = get_pending_emails(db)

        classified_emails: list[Email] = []

        for email in pending_emails:
            try:
                result = self.classify_email(
                    db=db,
                    email=email,
                )

                classified_emails.append(result)

            except Exception as exc:
                print(
                    f"❌ Failed to classify email "
                    f"{email.id}: {exc}"
                )

        return classified_emails