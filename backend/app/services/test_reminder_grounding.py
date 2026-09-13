from app.schemas.action_plan import (
    ActionType,
    ReminderActionPlan,
    RiskLevel,
)
from app.services.parameter_grounding import (
    validate_action_parameters,
)


def create_plan(
    reminder_text: str,
    reminder_date: str,
) -> ReminderActionPlan:
    return ReminderActionPlan(
        action=ActionType.CREATE_REMINDER,
        parameters={
            "reminder_text": reminder_text,
            "reminder_date": reminder_date,
        },
        reasoning="Test reminder.",
        confidence=0.95,
        risk_level=RiskLevel.LOW,
        requires_approval=False,
    )


def main() -> None:
    print("Testing Reminder Parameter Grounding")
    print("=" * 60)

    body = (
        "Your electricity bill of ₹2450 "
        "is due on September 20, 2026."
    )

    # -------------------------------------------------
    # Valid reminder
    # -------------------------------------------------

    valid_plan = create_plan(
        reminder_text="Pay electricity bill",
        reminder_date="2026-09-20",
    )

    valid_errors = validate_action_parameters(
        plan=valid_plan,
        subject="Electricity Bill",
        body=body,
    )

    print()
    print("VALID CASE")
    print("-" * 60)

    if not valid_errors:
        print("Grounding passed.")
    else:
        print("Grounding failed:")
        for error in valid_errors:
            print(f"- {error}")

    # -------------------------------------------------
    # Invalid reminder
    # -------------------------------------------------

    invalid_plan = create_plan(
        reminder_text="Book flight to Delhi",
        reminder_date="2027-04-15",
    )

    invalid_errors = validate_action_parameters(
        plan=invalid_plan,
        subject="Electricity Bill",
        body=body,
    )

    print()
    print("INVALID CASE")
    print("-" * 60)

    if invalid_errors:
        print("Grounding correctly failed:")
        for error in invalid_errors:
            print(f"- {error}")
    else:
        print("ERROR: Invalid reminder passed grounding.")


if __name__ == "__main__":
    main()