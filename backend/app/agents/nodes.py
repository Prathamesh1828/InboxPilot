from app.agents.state import InboxPilotState
from app.services.planner import EmailPlanner


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