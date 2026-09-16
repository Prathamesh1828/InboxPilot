from app.schemas.action_plan import (
    ActionType,
    ArchiveActionPlan,
    BillActionPlan,
    CalendarActionPlan,
    DraftReplyActionPlan,
    NoActionPlan,
    ReminderActionPlan,
    RiskLevel,
)
from app.services.action_safety import evaluate_action_safety


def test_safety_policy(
    name: str,
    plan,
    expected_risk: RiskLevel,
    expected_approval: bool,
) -> None:
    safe_plan = evaluate_action_safety(plan)

    passed = (
        safe_plan.risk_level == expected_risk
        and safe_plan.requires_approval == expected_approval
    )

    status = "PASS" if passed else "FAIL"

    print(
        f"{status}: {name:<30} "
        f"Risk={safe_plan.risk_level.value:<6} "
        f"Approval={safe_plan.requires_approval}"
    )

    if not passed:
        raise AssertionError(
            f"Safety policy failed for {name}"
        )


def main() -> None:
    print("Testing InboxPilot action safety policy")
    print("=" * 70)

    # -------------------------------------------------
    # LOG BILL
    # -------------------------------------------------

    bill_plan = BillActionPlan(
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

    # -------------------------------------------------
    # REMINDER
    # -------------------------------------------------

    reminder_plan = ReminderActionPlan(
        action=ActionType.CREATE_REMINDER,
        parameters={
            "reminder_text": "Pay electricity bill",
            "reminder_date": "2026-09-20",
        },
        reasoning="Test reminder action.",
        confidence=0.95,
        risk_level=RiskLevel.HIGH,
        requires_approval=True,
    )

    # -------------------------------------------------
    # CALENDAR EVENT
    # -------------------------------------------------

    calendar_plan = CalendarActionPlan(
        action=ActionType.CREATE_CALENDAR_EVENT,
        parameters={
            "title": "Client meeting",
            "start_time": "2026-09-20T10:00",
            "end_time": "2026-09-20T11:00",
            "description": "Discuss project requirements.",
        },
        reasoning="Test calendar action.",
        confidence=0.95,
        risk_level=RiskLevel.LOW,
        requires_approval=False,
    )

    # -------------------------------------------------
    # DRAFT REPLY
    # -------------------------------------------------

    draft_plan = DraftReplyActionPlan(
        action=ActionType.DRAFT_REPLY,
        parameters={
            "reply_text": "Thanks for reaching out. I will get back to you."
        },
        reasoning="Test draft reply.",
        confidence=0.95,
        risk_level=RiskLevel.LOW,
        requires_approval=False,
    )

    # -------------------------------------------------
    # ARCHIVE
    # -------------------------------------------------

    archive_plan = ArchiveActionPlan(
        action=ActionType.ARCHIVE,
        parameters={
            "reason": "Test archive action."
        },
        reasoning="Test archive action.",
        confidence=0.98,
        risk_level=RiskLevel.HIGH,
        requires_approval=True,
    )

    # -------------------------------------------------
    # NO ACTION
    # -------------------------------------------------

    no_action_plan = NoActionPlan(
        action=ActionType.NO_ACTION,
        reasoning="No action required.",
        confidence=0.99,
        risk_level=RiskLevel.HIGH,
        requires_approval=True,
    )

    # -------------------------------------------------
    # RUN TESTS
    # -------------------------------------------------

    print()
    print("SAFETY POLICY RESULTS")
    print("-" * 70)

    test_safety_policy(
        name="LOG_BILL",
        plan=bill_plan,
        expected_risk=RiskLevel.LOW,
        expected_approval=False,
    )

    test_safety_policy(
        name="CREATE_REMINDER",
        plan=reminder_plan,
        expected_risk=RiskLevel.LOW,
        expected_approval=False,
    )

    test_safety_policy(
        name="CREATE_CALENDAR_EVENT",
        plan=calendar_plan,
        expected_risk=RiskLevel.MEDIUM,
        expected_approval=True,
    )

    test_safety_policy(
        name="DRAFT_REPLY",
        plan=draft_plan,
        expected_risk=RiskLevel.MEDIUM,
        expected_approval=True,
    )

    test_safety_policy(
        name="ARCHIVE",
        plan=archive_plan,
        expected_risk=RiskLevel.LOW,
        expected_approval=False,
    )

    test_safety_policy(
        name="NO_ACTION",
        plan=no_action_plan,
        expected_risk=RiskLevel.LOW,
        expected_approval=False,
    )

    print()
    print("=" * 70)
    print("PASS: All safety policy tests passed")


if __name__ == "__main__":
    main()