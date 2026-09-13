from app.schemas.action_plan import (
    ActionType,
    RiskLevel,
    BillActionPlan,
)
from app.services.action_safety import evaluate_action_safety


def main() -> None:
    print("Testing InboxPilot action safety policy")
    print("=" * 60)

    test_plan = BillActionPlan(
        action=ActionType.LOG_BILL,
        parameters={
            "amount": 2450,
            "currency": "INR",
            "due_date": "2026-09-20",
        },
        reasoning="Test bill action.",
        confidence=0.97,
        risk_level=RiskLevel.HIGH,
        requires_approval=True,
    )

    print()
    print("LLM PROPOSED PLAN")
    print("-" * 60)
    print(f"Action:             {test_plan.action}")
    print(f"Risk level:         {test_plan.risk_level}")
    print(f"Requires approval:  {test_plan.requires_approval}")

    safe_plan = evaluate_action_safety(test_plan)

    print()
    print("AFTER SAFETY POLICY")
    print("-" * 60)
    print(f"Action:             {safe_plan.action}")
    print(f"Risk level:         {safe_plan.risk_level}")
    print(f"Requires approval:  {safe_plan.requires_approval}")

    print()
    print("=" * 60)

    if (
        safe_plan.risk_level == RiskLevel.LOW
        and safe_plan.requires_approval is False
    ):
        print("PASS: Safety policy test passed")
    else:
        print("FAIL: Safety policy test failed")


if __name__ == "__main__":
    main()