from app.agents.nodes import (
    grounding_node,
    review_node,
    route_after_grounding,
)
from app.agents.state import InboxPilotState
from app.schemas.action_plan import ActionPlan, ActionType, RiskLevel


def main() -> None:
    print("Testing grounding failure workflow")
    print("=" * 60)

    state = InboxPilotState(
        email_id=1002,
        subject="Electricity bill due September 20",
        body=(
            "Your electricity bill is ₹2450. "
            "Payment is due on September 20, 2026."
        ),
        action_plan=ActionPlan(
            action=ActionType.LOG_BILL,
            parameters={
                "amount": 2450,
                "currency": "INR",
                "due_date": "2026-09-20",
                "vendor": "Adani Electricity",
            },
            reasoning="Log the electricity bill.",
            confidence=0.97,
            risk_level=RiskLevel.LOW,
            requires_approval=False,
        ),
    )

    grounding_result = grounding_node(state)

    print()
    print("GROUNDING RESULT")
    print("-" * 60)

    print(f"Errors: {grounding_result['grounding_errors']}")
    print(f"Status: {grounding_result['workflow_status']}")

    updated_state = state.model_copy(
        update=grounding_result
    )

    route = route_after_grounding(updated_state)

    print()
    print("ROUTING RESULT")
    print("-" * 60)

    print(f"Route: {route}")

    if route == "review":
        review_result = review_node(updated_state)

        print()
        print("REVIEW RESULT")
        print("-" * 60)

        print(f"Status: {review_result['workflow_status']}")


if __name__ == "__main__":
    main()