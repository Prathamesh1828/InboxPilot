from app.schemas.action_plan import ActionPlan, ActionType, RiskLevel


def evaluate_action_safety(
    plan: ActionPlan,
) -> ActionPlan:
    """
    Apply InboxPilot's deterministic safety policy.

    The LLM may propose an action and risk level,
    but the application determines whether approval
    is actually required.
    """

    if plan.action in {
        ActionType.LOG_BILL,
        ActionType.CREATE_REMINDER,
        ActionType.ARCHIVE,
        ActionType.NO_ACTION,
    }:
        return plan.model_copy(
            update={
                "risk_level": RiskLevel.LOW,
                "requires_approval": False,
            }
        )

    if plan.action == ActionType.CREATE_CALENDAR_EVENT:
        return plan.model_copy(
            update={
                "risk_level": RiskLevel.MEDIUM,
                "requires_approval": True,
            }
        )

    if plan.action == ActionType.DRAFT_REPLY:
        return plan.model_copy(
            update={
                "risk_level": RiskLevel.MEDIUM,
                "requires_approval": True,
            }
        )

    return plan.model_copy(
        update={
            "risk_level": RiskLevel.HIGH,
            "requires_approval": True,
        }
    )