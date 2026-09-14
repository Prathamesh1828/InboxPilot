from sqlalchemy.orm import Session
from pydantic import TypeAdapter

from app.repositories.action_approval_repository import (
    get_action_approval,
)
from app.repositories.email_repository import (
    get_email_by_id,
)
from app.schemas.action_plan import ActionPlan
from app.services.action_safety import evaluate_action_safety
from app.services.executor import ActionExecutor
from app.services.parameter_grounding import (
    validate_action_parameters,
)


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
        # 2. Verify approval status
        # ---------------------------------------------

        if approval.status != "APPROVED":
            raise ValueError(
                f"Approval {approval_id} has status "
                f"{approval.status}. Only APPROVED actions "
                "can be executed."
            )

        # ---------------------------------------------
        # 3. Retrieve original email
        # ---------------------------------------------

        email = get_email_by_id(
            db=db,
            email_id=approval.email_id,
        )

        if email is None:
            raise ValueError(
                f"Email {approval.email_id} not found."
            )

        # ---------------------------------------------
        # 4. Reconstruct typed ActionPlan
        # ---------------------------------------------

        action_plan = TypeAdapter(ActionPlan).validate_python(
            approval.action_plan
        )

        # ---------------------------------------------
        # 5. Re-run parameter grounding
        # ---------------------------------------------

        grounding_errors = validate_action_parameters(
            plan=action_plan,
            subject=email.subject,
            body=email.body,
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

        return executor.execute(
            plan=safe_plan,
            db=db,
            email_id=email.id,
        )