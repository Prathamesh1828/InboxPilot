import logging

from sqlalchemy.orm import Session

from app.agents.state import InboxPilotState
from app.models.email import Email
from app.repositories.email_repository import get_email_by_id
from app.services.classification_service import ClassificationService
from app.services.workflow_service import WorkflowService
from app.schemas.classification import (
    EmailCategory,
    EmailClassification,
)
from app.repositories.audit_repository import log_audit_event

logger = logging.getLogger(__name__)


class EmailPipeline:
    def __init__(self) -> None:
        self.classification_service = ClassificationService()
        self.workflow_service = WorkflowService()

    def process_email(
        self,
        db: Session,
        email_id: int,
    ) -> InboxPilotState:
        """
        Run the complete InboxPilot processing pipeline.

        The pipeline is resumable.

        Flow:

            PENDING
              ↓
            Classification
              ↓
            Confidence Gate
              ↓
            REVIEW or CLASSIFIED
              ↓
            LangGraph workflow

        If classification has already completed and a later
        step fails, a retry can resume from CLASSIFIED instead
        of repeating classification.
        """

        # ---------------------------------------------------------
        # STEP 1: LOAD EMAIL
        # ---------------------------------------------------------

        email = get_email_by_id(
            db=db,
            email_id=email_id,
        )

        if email is None:
            raise ValueError(
                f"Email with ID {email_id} not found."
            )

        logger.info(
            "Email %d loaded (status=%s)",
            email_id,
            email.status,
        )

        # ---------------------------------------------------------
        # STEP 2: HANDLE CLASSIFICATION
        # ---------------------------------------------------------

        if email.status == "PENDING":
            log_audit_event(
                db=db,
                email_id=email_id,
                event_type="EMAIL_RECEIVED",
                status="PENDING",
            )
            
            logger.info(
                "Classifying email %d",
                email_id,
            )

            email = self.classification_service.classify_email(
                db=db,
                email=email,
            )

            logger.info(
                "Email %d classified: category=%s confidence=%.2f status=%s",
                email_id,
                email.category,
                email.classification_confidence or 0.0,
                email.status,
            )
            
            log_audit_event(
                db=db,
                email_id=email_id,
                event_type="CLASSIFICATION_COMPLETED",
                status=email.status,
                details={
                    "category": email.category,
                    "confidence": email.classification_confidence,
                    "reasoning": email.classification_reasoning,
                },
            )

        elif email.status == "CLASSIFIED":
            logger.info(
                "Email %d already classified, resuming workflow",
                email_id,
            )

        elif email.status == "REVIEW":
            logger.info(
                "Email %d is awaiting human review",
                email_id,
            )

            return self._build_review_state(email)

        else:
            raise ValueError(
                f"Email {email_id} cannot enter the pipeline. "
                f"Current status: {email.status}"
            )

        # ---------------------------------------------------------
        # STEP 3: CONFIDENCE GATE
        # ---------------------------------------------------------

        if email.status == "REVIEW":
            logger.info(
                "Email %d requires human review, stopping",
                email_id,
            )

            return self._build_review_state(email)

        if email.status != "CLASSIFIED":
            raise ValueError(
                f"Unexpected classification status for "
                f"email {email_id}: {email.status}"
            )

        # ---------------------------------------------------------
        # STEP 4: ACTION WORKFLOW
        # ---------------------------------------------------------

        logger.info(
            "Email %d passed confidence gate, starting workflow",
            email_id,
        )

        workflow_result = self.workflow_service.process_email(
            db=db,
            email_id=email_id,
        )

        # ---------------------------------------------------------
        # STEP 5: WORKFLOW RESULT
        # ---------------------------------------------------------

        logger.info(
            "Email %d workflow completed: status=%s action=%s approval_id=%s",
            email_id,
            workflow_result.workflow_status,
            (
                workflow_result.action_plan.action.value
                if workflow_result.action_plan is not None
                else None
            ),
            workflow_result.approval_id,
        )

        log_audit_event(
            db=db,
            email_id=email_id,
            event_type="WORKFLOW_COMPLETED",
            status=workflow_result.workflow_status,
            action=(
                workflow_result.action_plan.action.value
                if workflow_result.action_plan is not None
                else None
            ),
            approval_id=workflow_result.approval_id,
            details={
                "error": workflow_result.error,
                "execution_result": workflow_result.execution_result,
            }
        )

        if workflow_result.error is not None:
            logger.warning(
                "Email %d workflow error: %s",
                email_id,
                workflow_result.error,
            )

        return workflow_result

    @staticmethod
    def _build_review_state(
        email: Email,
    ) -> InboxPilotState:
        """
        Build a pipeline state for an email that requires
        human review.
        """

        return InboxPilotState(
            email_id=email.id,
            subject=email.subject,
            body=email.body,
            workflow_status="REVIEW",
            error=(
                "Email classification confidence is below "
                "the threshold."
            ),
            classification=(
                EmailClassification(
                    category=EmailCategory(email.category),
                    confidence=email.classification_confidence
                    or 0.0,
                    reasoning=email.classification_reasoning
                    or "Classification requires human review.",
                )
                if email.category is not None
                else None
            ),
        )