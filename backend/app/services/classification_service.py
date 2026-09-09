from sqlalchemy.orm import Session

from app.models.email import Email
from app.repositories.email_repository import update_email_classification
from app.services.classification_gate import evaluate_classification
from app.services.classifier import EmailClassifier


class ClassificationService:
    """
    Coordinates the complete email classification workflow.

    Flow:

        Email from database
                ↓
        EmailClassifier
                ↓
        Groq
                ↓
        Gemini fallback if required
                ↓
        Classification Gate
                ↓
        CLASSIFIED / REVIEW
                ↓
        Database
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

        # --------------------------------------------------------
        # 1. Run the LLM classifier
        # --------------------------------------------------------

        classification = self.classifier.classify(
            sender=email.sender,
            recipients=email.recipients,
            subject=email.subject or "",
            body=email.body,
        )

        # --------------------------------------------------------
        # 2. Evaluate confidence
        # --------------------------------------------------------

        status = evaluate_classification(
            classification
        )

        # --------------------------------------------------------
        # 3. Persist classification result
        # --------------------------------------------------------

        updated_email = update_email_classification(
            db=db,
            email=email,
            classification=classification,
            status=status,
        )

        return updated_email