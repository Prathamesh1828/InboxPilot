from app.agents.graph import build_planning_graph
from app.schemas.classification import EmailCategory, EmailClassification


def main() -> None:
    print("Testing InboxPilot LangGraph")
    print("=" * 60)

    graph = build_planning_graph()

    initial_state = {
        "email_id": 999,
        "subject": "Electricity bill due September 20",
        "body": (
            "Your electricity bill of ₹2450 is due on "
            "September 20, 2026."
        ),
        "classification": EmailClassification(
            category=EmailCategory.BILL,
            confidence=0.97,
            reasoning=(
                "The email contains a payment amount "
                "and a due date."
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