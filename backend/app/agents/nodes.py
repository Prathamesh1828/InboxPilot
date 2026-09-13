from app.agents.state import InboxPilotState
from app.services.planner import EmailPlanner
from app.services.action_safety import evaluate_action_safety


def safety_node(
    state: InboxPilotState,
) -> dict:
    """
    Apply the deterministic safety policy
    to the proposed action plan.
    """

    action_plan = state.action_plan

    if action_plan is None:
        raise ValueError(
            "Action plan is required before safety evaluation"
        )

    safe_plan = evaluate_action_safety(action_plan)

    return {
        "action_plan": safe_plan,
        "workflow_status": "SAFETY_EVALUATED",
    }


def planning_node(
    state: InboxPilotState,
) -> dict:
    """
    Create an action plan for the classified email.
    """

    classification = state.classification

    if classification is None:
        raise ValueError(
            "Classification is required before planning"
        )

    planner = EmailPlanner()

    action_plan = planner.create_plan(
        category=classification.category.value,
        classification_reasoning=classification.reasoning,
        subject=state.subject,
        body=state.body,
    )

    return {
        "action_plan": action_plan,
        "workflow_status": "PLANNED",
    }

def safety_node(
    state: InboxPilotState,
) -> dict:
    """
    Apply the deterministic safety policy
    to the proposed action plan.
    """

    action_plan = state.action_plan

    if action_plan is None:
        raise ValueError(
            "Action plan is required before safety evaluation"
        )

    safe_plan = evaluate_action_safety(action_plan)

    return {
        "action_plan": safe_plan,
        "workflow_status": "SAFETY_EVALUATED",
    }

def route_after_safety(
    state: InboxPilotState,
) -> str:
    """
    Decide where the workflow should go
    after safety evaluation.
    """

    action_plan = state.action_plan

    if action_plan is None:
        raise ValueError(
            "Action plan is required for routing"
        )

    if action_plan.requires_approval:
        return "approval"

    return "execute"

def execute_node(
    state: InboxPilotState,
) -> dict:
    """
    Placeholder for executing a safe action.

    No real external action is performed yet.
    """

    return {
        "workflow_status": "EXECUTION_PENDING",
    }


def approval_node(
    state: InboxPilotState,
) -> dict:
    """
    Placeholder for requesting human approval.

    No real notification is sent yet.
    """

    return {
        "workflow_status": "APPROVAL_PENDING",
    }