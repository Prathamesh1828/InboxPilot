from app.services.planner import EmailPlanner


def main() -> None:
    print("Testing LangChain email planner")
    print("=" * 60)

    planner = EmailPlanner()

    plan = planner.create_plan(
        category="BILL",
        classification_reasoning=(
            "The email contains a payment amount and a due date."
        ),
        subject="Electricity bill due September 20",
        body=(
            "Your electricity bill of ₹2450 is due on "
            "September 20, 2026."
        ),
    )

    print()
    print("PLANNER RESULT")
    print("-" * 60)

    print(f"Action:             {plan.action}")
    print(f"Parameters:        {plan.parameters}")
    print(f"Reasoning:         {plan.reasoning}")
    print(f"Confidence:        {plan.confidence}")
    print(f"Risk level:        {plan.risk_level}")
    print(f"Requires approval: {plan.requires_approval}")


if __name__ == "__main__":
    main()