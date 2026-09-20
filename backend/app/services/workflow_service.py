import logging
from sqlalchemy.orm import Session

from app.agents.graph import build_planning_graph
from app.agents.state import InboxPilotState
from app.models.email import Email
from app.repositories.email_repository import get_email_by_id

logger = logging.getLogger(__name__)


class WorkflowService:
    def process_email(
        self,
        db: Session,
        email_id: int,
    ) -> InboxPilotState:

        email = get_email_by_id(db, email_id)

        if email is None:
            raise ValueError(f"Email with ID {email_id} not found.")

        # Only classified emails are allowed to enter the action workflow.
        if email.status != "CLASSIFIED":
            raise ValueError(
                f"Email {email_id} cannot enter the planning workflow. "
                f"Current status: {email.status}"
            )

        if email.category is None:
            raise ValueError(
                f"Email {email_id} is marked CLASSIFIED but has no category."
            )

        if email.classification_reasoning is None:
            raise ValueError(
                f"Email {email_id} is marked CLASSIFIED but has no "
                "classification reasoning."
            )

        state = InboxPilotState(
            email_id=email.id,
            subject=email.subject,
            body=email.body,
            received_at=email.received_at,
        )

        # Reconstruct the classification object from the database.
        from app.schemas.classification import (
            EmailCategory,
            EmailClassification,
        )

        state.classification = EmailClassification(
            category=EmailCategory(email.category),
            confidence=email.classification_confidence or 0.0,
            reasoning=email.classification_reasoning,
        )

        logger.info(
            "Invoking planning graph for email %d",
            email_id,
        )

        graph = build_planning_graph(db)

        result = graph.invoke(state)

        return InboxPilotState.model_validate(result)