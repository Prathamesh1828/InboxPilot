from app.agents.nodes import grounding_node
from app.agents.state import InboxPilotState
from app.schemas.action_plan import ActionType, RiskLevel, BillActionPlan


def main() -> None:
    print("Testing LangGraph grounding node")
    print("=" * 60)

    state = InboxPilotState(
        email_id=1001,
        subject="Electricity bill",
        body=(
            "Your electricity bill is ₹2450. "
            "Payment is due on September 20, 2026."
        ),
        action_plan=BillActionPlan(
            action=ActionType.LOG_BILL,
            parameters={
                "amount": 2450,
                "currency": "INR",
                "due_date": "2026-09-20",
                "vendor": "electricity",
            },
            reasoning="Log the electricity bill.",
            confidence=0.97,
            risk_level=RiskLevel.LOW,
            requires_approval=False,
        ),
    )

    # pyrefly: ignore [missing-argument]
    result = grounding_node(state)

    print()
    print("GROUNDING NODE RESULT")
    print("-" * 60)
    print(f"Errors: {result['grounding_errors']}")
    print(f"Status: {result['workflow_status']}")


if __name__ == "__main__":
    main()