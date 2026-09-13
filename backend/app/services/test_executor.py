from datetime import date

from app.db.database import SessionLocal
from app.schemas.action_plan import (
    ActionPlan,
    ActionType,
    RiskLevel,
)
from app.services.executor import ActionExecutor


def main() -> None:
    print("Testing InboxPilot Action Executor")
    print("=" * 60)

    db = SessionLocal()

    try:
        plan = ActionPlan(
            action=ActionType.LOG_BILL,
            parameters={
                "amount": 2450,
                "currency": "INR",
                "vendor": "Electricity",
                "due_date": "2026-09-20",
            },
            reasoning="Test bill execution.",
            confidence=0.98,
            risk_level=RiskLevel.LOW,
            requires_approval=False,
        )

        executor = ActionExecutor()

        result = executor.execute(
            plan=plan,
            db=db,
            email_id=1,
        )

        print()
        print("EXECUTOR RESULT")
        print("-" * 60)
        print(result)

    finally:
        db.close()


if __name__ == "__main__":
    main()