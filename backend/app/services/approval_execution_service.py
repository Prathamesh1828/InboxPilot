import logging
from sqlalchemy.orm import Session
from pydantic import TypeAdapter

from app.repositories.action_approval_repository import (
    atomic_transition_status,
    get_action_approval,
    update_action_approval_status,
)
from app.repositories.email_repository import (
    get_email_by_id,
    mark_email_processed,
)
from app.schemas.action_plan import ActionPlan
from app.services.action_safety import evaluate_action_safety
from app.services.executor import ActionExecutor
from app.services.parameter_grounding import (
    validate_action_parameters,
)

logger = logging.getLogger(__name__)


class ApprovalExecutionService:
    """
    Executes an action after human approval.

    An approved action is reconstructed from the persisted
    action plan and validated again before execution.
    """

    @staticmethod
    def execute_approved(
        db: Session,
        approval_id: int,
    ) -> str:
        # ---------------------------------------------
        # 1. Retrieve approval
        # ---------------------------------------------

        approval = get_action_approval(
            db=db,
            approval_id=approval_id,
        )

        if approval is None:
            raise ValueError(
                f"Approval {approval_id} not found."
            )

        # ---------------------------------------------
        # 2. Atomic status transition: APPROVED → EXECUTING
        #
        # This is a filtered UPDATE so only ONE caller
        # wins when two requests race on the same approval.
        # ---------------------------------------------

        transitioned = atomic_transition_status(
            db=db,
            approval_id=approval_id,
            from_status="APPROVED",
            to_status="EXECUTING",
        )

        if not transitioned:
            # Either already executing, executed, or not approved
            db.refresh(approval)
            raise ValueError(
                f"Approval {approval_id} cannot be executed. "
                f"Current status: {approval.status}. "
                "Only APPROVED actions can be executed."
            )

        # ---------------------------------------------
        # 3. Retrieve original email
        # ---------------------------------------------

        email = get_email_by_id(
            db=db,
            email_id=approval.email_id,
        )

        if email is None:
            update_action_approval_status(
                db=db,
                approval_id=approval_id,
                status="EXECUTION_FAILED",
            )
            raise ValueError(
                f"Email {approval.email_id} not found."
            )

        # ---------------------------------------------
        # 4. Reconstruct typed ActionPlan
        # ---------------------------------------------

        action_plan = TypeAdapter(ActionPlan).validate_python(
            approval.action_plan
        )

        try:
            # ---------------------------------------------
            # 5. Re-run parameter grounding
            # ---------------------------------------------
            logger.info(
                "Validating action parameters for approval %d",
                approval_id,
            )

            grounding_errors = validate_action_parameters(
                plan=action_plan,
                subject=email.subject,
                body=email.body,
                reference_time=email.received_at,
            )

            if grounding_errors:
                raise ValueError(
                    "Approved action failed grounding validation: "
                    + "; ".join(grounding_errors)
                )

            # ---------------------------------------------
            # 6. Re-evaluate deterministic safety
            # ---------------------------------------------

            safe_plan = evaluate_action_safety(
                action_plan
            )

            # ---------------------------------------------
            # 7. Execute through existing executor
            # ---------------------------------------------

            executor = ActionExecutor()
            
            logger.info(
                "Executing action %s for approval %d",
                safe_plan.action.value,
                approval_id,
            )

            result = executor.execute(
                plan=safe_plan,
                db=db,
                email_id=email.id,
            )
        except Exception as exc:
            logger.error(
                "Execution failed for approval %d, marking EXECUTION_FAILED: %s",
                approval_id,
                exc,
            )
            update_action_approval_status(
                db=db,
                approval_id=approval_id,
                status="EXECUTION_FAILED",
            )
            from app.repositories.email_repository import update_email_status
            update_email_status(db, email, "FAILED")
            raise exc

        # ---------------------------------------------
        # 8. Update state
        # ---------------------------------------------

        logger.info(
            "Execution successful for approval %d, updating state",
            approval_id,
        )

        update_action_approval_status(
            db=db,
            approval_id=approval_id,
            status="EXECUTED",
        )

        mark_email_processed(
            db=db,
            email=email,
        )

        return result