from app.schemas.action_plan import (
    ActionPlan,
    ActionType,
    RiskLevel,
)
from app.services.executor import ActionExecutor


def create_plan(
    action: ActionType,
    parameters: dict[str, str | int | float | bool | None],
) -> ActionPlan:
    return ActionPlan(
        action=action,
        parameters=parameters,
        reasoning="Test action.",
        confidence=0.95,
        risk_level=RiskLevel.LOW,
        requires_approval=False,
    )


def main() -> None:
    print("Testing InboxPilot Executor Actions")
    print("=" * 60)

    executor = ActionExecutor()

    plans = [
        create_plan(
            ActionType.LOG_BILL,
            {
                "amount": 2450,
                "currency": "INR",
                "due_date": "2026-09-20",
            },
        ),
        create_plan(
            ActionType.CREATE_REMINDER,
            {
                "reminder_text": "Pay electricity bill",
                "reminder_date": "2026-09-20",
            },
        ),
        create_plan(
            ActionType.ARCHIVE,
            {},
        ),
        create_plan(
            ActionType.NO_ACTION,
            {},
        ),
    ]

    for plan in plans:
        print()
        print(f"Action: {plan.action}")

        result = executor.execute(plan)

        print(f"Result: {result}")


if __name__ == "__main__":
    main()