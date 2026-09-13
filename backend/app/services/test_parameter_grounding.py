from app.schemas.action_plan import ActionPlan, ActionType, RiskLevel
from app.services.parameter_grounding import validate_action_parameters


def main() -> None:
    print("Testing parameter grounding")
    print("=" * 60)

    email_body = (
        "Your electricity bill is ₹2450. "
        "Payment is due on September 20, 2026."
    )

    plan = ActionPlan(
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
    )

    errors = validate_action_parameters(
        plan=plan,
        subject="Electricity bill",
        body=email_body,
    )

    print()
    print("GROUNDING RESULT")
    print("-" * 60)

    if errors:
        print("❌ Grounding failed")

        for error in errors:
            print(f"- {error}")

    else:
        print("✅ All parameters are grounded")


if __name__ == "__main__":
    main()