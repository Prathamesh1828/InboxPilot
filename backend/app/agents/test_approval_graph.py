from app.agents.graph import build_planning_graph
from app.agents.state import InboxPilotState
from app.db.database import SessionLocal
from app.repositories.action_approval_repository import (
    get_action_approval,
)
from app.schemas.classification import (
    EmailCategory,
    EmailClassification,
)


def main() -> None:
    print("Testing InboxPilot Approval LangGraph")
    print("=" * 60)

    db = SessionLocal()

    try:
        state = InboxPilotState(
            email_id=2,
            subject="Meeting Request",
            body=(
                "Hi, can we schedule a meeting tomorrow "
                "at 10 AM to discuss the project?"
            ),
            classification=EmailClassification(
                category=EmailCategory.MEETING,
                confidence=0.98,
                reasoning=(
                    "The email contains a request to schedule "
                    "a meeting."
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
            print(f"Risk level:         {action_plan.risk_level}")
            print(
                f"Requires approval:  "
                f"{action_plan.requires_approval}"
            )

        approval_id = result.get("approval_id")

        print(f"Approval ID:        {approval_id}")
        print(
            f"Workflow status:    "
            f"{result.get('workflow_status')}"
        )

        if approval_id is None:
            raise AssertionError(
                "Approval ID was not created."
            )

        approval = get_action_approval(
            db=db,
            approval_id=approval_id,
        )

        if approval is None:
            raise AssertionError(
                "Approval record was not found in database."
            )

        if approval.status != "PENDING":
            raise AssertionError(
                f"Expected PENDING, got {approval.status}."
            )

        if result.get("workflow_status") != "APPROVAL_PENDING":
            raise AssertionError(
                "Workflow did not enter APPROVAL_PENDING."
            )

        print()
        print("APPROVAL VERIFICATION")
        print("-" * 60)
        print("Approval record created successfully.")
        print(f"Approval ID: {approval.id}")
        print(f"Status:      {approval.status}")
        print(f"Action:      {approval.action}")

        print()
        print("Approval graph test passed.")

    finally:
        db.close()


if __name__ == "__main__":
    main()