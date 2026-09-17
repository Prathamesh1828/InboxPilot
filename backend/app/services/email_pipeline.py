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

        print(
            f"[Pipeline] Email {email_id} loaded. "
            f"Current status: {email.status}"
        )

        # ---------------------------------------------------------
        # STEP 2: HANDLE CLASSIFICATION
        # ---------------------------------------------------------

        if email.status == "PENDING":
            print(
                f"[Pipeline] Starting classification "
                f"for email {email_id}..."
            )

            email = self.classification_service.classify_email(
                db=db,
                email=email,
            )

            print(
                f"[Pipeline] Classification completed for "
                f"email {email_id}."
            )

            print(
                f"[Pipeline] Category: {email.category}"
            )

            print(
                f"[Pipeline] Confidence: "
                f"{email.classification_confidence}"
            )

            print(
                f"[Pipeline] Status after classification: "
                f"{email.status}"
            )

        elif email.status == "CLASSIFIED":
            print(
                f"[Pipeline] Email {email_id} is already classified."
            )

            print(
                "[Pipeline] Skipping classification and "
                "resuming workflow."
            )

        elif email.status == "REVIEW":
            print(
                f"[Pipeline] Email {email_id} is already "
                "waiting for human review."
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
            print(
                f"[Pipeline] Email {email_id} requires human review."
            )

            print(
                f"[Pipeline] Stopping processing for email {email_id}."
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

        print(
            f"[Pipeline] Email {email_id} passed "
            "the confidence gate."
        )

        print(
            f"[Pipeline] Starting action workflow "
            f"for email {email_id}..."
        )

        workflow_result = self.workflow_service.process_email(
            db=db,
            email_id=email_id,
        )

        # ---------------------------------------------------------
        # STEP 5: WORKFLOW RESULT
        # ---------------------------------------------------------

        print(
            f"[Pipeline] Action workflow completed "
            f"for email {email_id}."
        )

        print(
            f"[Pipeline] Workflow status: "
            f"{workflow_result.workflow_status}"
        )

        if workflow_result.action_plan is not None:
            print(
                f"[Pipeline] Action: "
                f"{workflow_result.action_plan.action}"
            )

            print(
                f"[Pipeline] Risk level: "
                f"{workflow_result.action_plan.risk_level}"
            )

            print(
                f"[Pipeline] Requires approval: "
                f"{workflow_result.action_plan.requires_approval}"
            )

        if workflow_result.approval_id is not None:
            print(
                f"[Pipeline] Approval ID: "
                f"{workflow_result.approval_id}"
            )

        if workflow_result.execution_result is not None:
            print(
                f"[Pipeline] Execution result: "
                f"{workflow_result.execution_result}"
            )

        if workflow_result.error is not None:
            print(
                f"[Pipeline] Workflow error: "
                f"{workflow_result.error}"
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