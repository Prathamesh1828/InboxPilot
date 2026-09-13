from app.schemas.action_plan import (
    ActionPlan,
    ActionType,
    RiskLevel,
    BillActionPlan,
    ReminderActionPlan,
    ArchiveActionPlan,
    NoActionPlan,
)
from app.db.database import SessionLocal
from app.services.executor import ActionExecutor

def main() -> None:
    print("Testing InboxPilot Executor Actions")
    print("=" * 60)

    db = SessionLocal()
    
    try:
        executor = ActionExecutor()

        plans = [
            BillActionPlan(
                action=ActionType.LOG_BILL,
                parameters={
                    "amount": 2450,
                    "currency": "INR",
                    "due_date": "2026-09-20",
                },
                reasoning="Test action.",
                confidence=0.95,
                risk_level=RiskLevel.LOW,
                requires_approval=False,
            ),
            ReminderActionPlan(
                action=ActionType.CREATE_REMINDER,
                parameters={
                    "reminder_text": "Pay electricity bill",
                    "reminder_date": "2026-09-20",
                },
                reasoning="Test action.",
                confidence=0.95,
                risk_level=RiskLevel.LOW,
                requires_approval=False,
            ),
            ArchiveActionPlan(
                action=ActionType.ARCHIVE,
                parameters={},
                reasoning="Test action.",
                confidence=0.95,
                risk_level=RiskLevel.LOW,
                requires_approval=False,
            ),
            NoActionPlan(
                action=ActionType.NO_ACTION,
                parameters={},
                reasoning="Test action.",
                confidence=0.95,
                risk_level=RiskLevel.LOW,
                requires_approval=False,
            ),
        ]

        for plan in plans:
            print()
            print(f"Action: {plan.action}")

            result = executor.execute(plan, db=db, email_id=1)

            print(f"Result: {result}")
            
    finally:
        db.close()


if __name__ == "__main__":
    main()