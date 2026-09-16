from app.schemas.action_plan import (
    ActionType,
    DraftReplyActionPlan,
    RiskLevel,
)
from app.services.parameter_grounding import validate_action_parameters


def main() -> None:
    print("Testing draft reply parameter grounding")
    print("=" * 60)

    email_body = (
        "Hi, I wanted to ask about the internship application. "
        "Could you please let me know the application deadline "
        "and the required documents?"
    )

    # -------------------------------------------------
    # TEST 1: VALID REPLY
    # -------------------------------------------------

    valid_plan = DraftReplyActionPlan(
        action=ActionType.DRAFT_REPLY,
        parameters={
            "reply_text": (
                "Hi, thanks for reaching out. "
                "I will check the internship application deadline "
                "and the required documents."
            ),
        },
        reasoning="Reply to the internship application question.",
        confidence=0.95,
        risk_level=RiskLevel.MEDIUM,
        requires_approval=True,
    )

    valid_errors = validate_action_parameters(
        plan=valid_plan,
        subject="Internship Application",
        body=email_body,
    )

    print()
    print("TEST 1: VALID REPLY")
    print("-" * 60)

    if valid_errors:
        print("FAIL: Valid reply was rejected")

        for error in valid_errors:
            print(f"- {error}")
    else:
        print("PASS: Valid reply was accepted")

    # -------------------------------------------------
    # TEST 2: UNRELATED REPLY
    # -------------------------------------------------

    invalid_plan = DraftReplyActionPlan(
        action=ActionType.DRAFT_REPLY,
        parameters={
            "reply_text": (
                "Your order has been shipped and will arrive tomorrow."
            ),
        },
        reasoning="Reply to the email.",
        confidence=0.95,
        risk_level=RiskLevel.MEDIUM,
        requires_approval=True,
    )

    invalid_errors = validate_action_parameters(
        plan=invalid_plan,
        subject="Internship Application",
        body=email_body,
    )

    print()
    print("TEST 2: UNRELATED REPLY")
    print("-" * 60)

    if invalid_errors:
        print("PASS: Unrelated reply was correctly rejected")

        for error in invalid_errors:
            print(f"- {error}")
    else:
        print("FAIL: Unrelated reply was incorrectly accepted")


if __name__ == "__main__":
    main()