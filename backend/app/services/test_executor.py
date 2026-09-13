from app.db.database import SessionLocal
from app.schemas.action_plan import (
    ActionType,
    BillActionPlan,
    ReminderActionPlan,
    RiskLevel,
)
from app.services.executor import ActionExecutor


def main() -> None:
    print("Testing InboxPilot Action Executor")
    print("=" * 60)

    db = SessionLocal()

    try:
        executor = ActionExecutor()

        # -------------------------------------------------
        # LOG_BILL
        # -------------------------------------------------

        bill_plan = BillActionPlan(
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

        bill_result = executor.execute(
            plan=bill_plan,
            db=db,
            email_id=1,
        )

        print()
        print("LOG_BILL RESULT")
        print("-" * 60)
        print(bill_result)

        # -------------------------------------------------
        # CREATE_REMINDER
        # -------------------------------------------------

        reminder_plan = ReminderActionPlan(
            action=ActionType.CREATE_REMINDER,
            parameters={
                "reminder_text": "Pay electricity bill",
                "reminder_date": "2026-09-20",
            },
            reasoning="Test reminder execution.",
            confidence=0.98,
            risk_level=RiskLevel.LOW,
            requires_approval=False,
        )

        reminder_result = executor.execute(
            plan=reminder_plan,
            db=db,
            email_id=2,
        )

        print()
        print("CREATE_REMINDER RESULT")
        print("-" * 60)
        print(reminder_result)

        # -------------------------------------------------
        # CREATE_REMINDER AGAIN
        # -------------------------------------------------

        reminder_repeat_result = executor.execute(
            plan=reminder_plan,
            db=db,
            email_id=2,
        )

        print()
        print("CREATE_REMINDER IDEMPOTENCY RESULT")
        print("-" * 60)
        print(reminder_repeat_result)

    finally:
        db.close()


if __name__ == "__main__":
    main()