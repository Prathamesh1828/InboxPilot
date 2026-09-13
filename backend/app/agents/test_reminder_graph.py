import app.models

from app.agents.graph import build_planning_graph
from app.agents.state import InboxPilotState
from app.db.database import SessionLocal
from app.schemas.classification import (
    EmailCategory,
    EmailClassification,
)


def main() -> None:
    print("Testing InboxPilot Reminder LangGraph")
    print("=" * 60)

    db = SessionLocal()

    try:
        state = InboxPilotState(
            email_id=2,
            subject="Electricity Bill Reminder",
            body=(
                "Your electricity bill of ₹2450 "
                "is due on September 20, 2026. "
                "Please make the payment before the due date."
            ),
            classification=EmailClassification(
                category=EmailCategory.REMINDER,
                confidence=0.98,
                reasoning=(
                    "The email contains a future payment "
                    "deadline that should be remembered."
                ),
            ),
        )

        graph = build_planning_graph(db)

        print()
        print("Running reminder graph...")
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