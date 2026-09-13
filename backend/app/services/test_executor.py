from app.schemas.action_plan import (
    ActionPlan,
    ActionType,
    RiskLevel,
)
from app.services.executor import ActionExecutor


def main() -> None:
    print("Testing InboxPilot Action Executor")
    print("=" * 60)

    plan = ActionPlan(
        action=ActionType.LOG_BILL,
        parameters={
            "amount": 2450,
            "currency": "INR",
            "due_date": "2026-09-20",
        },
        reasoning="Log the electricity bill.",
        confidence=0.97,
        risk_level=RiskLevel.LOW,
        requires_approval=False,
    )

    executor = ActionExecutor()

    result = executor.execute(plan)

    print()
    print("EXECUTOR RESULT")
    print("-" * 60)
    print(result)


if __name__ == "__main__":
    main()