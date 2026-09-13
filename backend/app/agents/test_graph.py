import app.models

from app.agents.graph import build_planning_graph
from app.agents.state import InboxPilotState
from app.db.database import SessionLocal
from app.schemas.classification import (
    EmailCategory,
    EmailClassification,
)


def main() -> None:
    print("Testing InboxPilot LangGraph")
    print("=" * 60)

    db = SessionLocal()

    try:
        state = InboxPilotState(
            email_id=1,
            subject="Electricity Bill",
            body=(
                "Your electricity bill is ₹2450. "
                "Payment is due on September 20, 2026."
            ),
            classification=EmailClassification(
                category=EmailCategory.BILL,
                confidence=0.98,
                reasoning=(
                    "The email contains a bill amount "
                    "and a payment due date."
                ),
            ),
        )

        graph = build_planning_graph(db)

        print()
        print("Running graph...")
        print()

        result = graph.invoke(state)

        print("GRAPH RESULT")
        print("-" * 60)

        action_plan = result.get("action_plan")

        if action_plan is not None:
            print(f"Action:             {action_plan.action}")
            print(f"Parameters:         {action_plan.parameters}")
            print(f"Reasoning:          {action_plan.reasoning}")
            print(f"Confidence:         {action_plan.confidence}")
            print(f"Risk level:         {action_plan.risk_level}")
            print(
                f"Requires approval:  "
                f"{action_plan.requires_approval}"
            )

        print(
            f"Grounding errors:   "
            f"{result.get('grounding_errors')}"
        )

        print(
            f"Execution result:   "
            f"{result.get('execution_result')}"
        )

        print(
            f"Workflow status:    "
            f"{result.get('workflow_status')}"
        )

    finally:
        db.close()


if __name__ == "__main__":
    main()