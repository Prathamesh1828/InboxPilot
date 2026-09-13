from app.agents.graph import build_planning_graph
from app.schemas.classification import EmailCategory, EmailClassification


def main() -> None:
    print("Testing InboxPilot LangGraph")
    print("=" * 60)

    graph = build_planning_graph()

    initial_state = {
    "email_id": 1000,
    "subject": "Interview availability",
    "body": (
        "Hi, we would like to schedule an interview. "
        "Please let us know your availability."
    ),
    "classification": EmailClassification(
        category=EmailCategory.MEETING,
        confidence=0.96,
        reasoning=(
            "The email is requesting interview scheduling."
        ),
    ),
    "workflow_status": "CLASSIFIED",
}

    print()
    print("Running graph...")
    print()

    result = graph.invoke(initial_state)

    print("GRAPH RESULT")
    print("-" * 60)

    action_plan = result["action_plan"]

    print(f"Action:             {action_plan.action}")
    print(f"Parameters:         {action_plan.parameters}")
    print(f"Reasoning:          {action_plan.reasoning}")
    print(f"Confidence:         {action_plan.confidence}")
    print(f"Risk level:         {action_plan.risk_level}")
    print(
        f"Requires approval:  "
        f"{action_plan.requires_approval}"
    )
    print(f"Workflow status:    {result['workflow_status']}")


if __name__ == "__main__":
    main()