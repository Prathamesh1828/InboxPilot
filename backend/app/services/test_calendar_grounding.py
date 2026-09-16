from app.schemas.action_plan import (
    ActionType,
    CalendarActionPlan,
    RiskLevel,
)
from app.services.parameter_grounding import validate_action_parameters


def main() -> None:
    print("Testing calendar parameter grounding")
    print("=" * 60)

    email_body = (
        "Meeting with the client is scheduled for "
        "September 20, 2026 at 10:00. "
        "We will discuss the new project requirements."
    )

    plan = CalendarActionPlan(
        action=ActionType.CREATE_CALENDAR_EVENT,
        parameters={
            "title": "Client meeting",
            "start_time": "2026-09-20T10:00",
            "end_time": None,
            "description": "Discuss the new project requirements.",
        },
        reasoning="Create a calendar event for the client meeting.",
        confidence=0.95,
        risk_level=RiskLevel.MEDIUM,
        requires_approval=True,
    )

    errors = validate_action_parameters(
        plan=plan,
        subject="Client Meeting",
        body=email_body,
    )

    print()
    print("GROUNDING RESULT")
    print("-" * 60)

    if errors:
        print("FAIL: Grounding failed")

        for error in errors:
            print(f"- {error}")

    else:
        print("PASS: All calendar parameters are grounded")


if __name__ == "__main__":
    main()