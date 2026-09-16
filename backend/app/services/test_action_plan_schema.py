from pydantic import ValidationError

from app.schemas.action_plan import (
    BillParameters,
    CalendarEventParameters,
    DraftReplyParameters,
    NoActionParameters,
    ReminderParameters,
    ArchiveParameters,
)


def test_extra_fields_are_rejected() -> None:
    print("Testing ActionPlan parameter schema hardening")
    print("=" * 60)

    parameter_models = [
        (
            "BillParameters",
            BillParameters,
            {
                "amount": 2450,
                "currency": "INR",
                "unexpected_field": "test",
            },
        ),
        (
            "ReminderParameters",
            ReminderParameters,
            {
                "reminder_text": "Pay bill",
                "reminder_date": "2026-09-20",
                "unexpected_field": "test",
            },
        ),
        (
            "CalendarEventParameters",
            CalendarEventParameters,
            {
                "title": "Client meeting",
                "start_time": "2026-09-20T10:00",
                "unexpected_field": "test",
            },
        ),
        (
            "DraftReplyParameters",
            DraftReplyParameters,
            {
                "reply_text": "Thanks for reaching out.",
                "unexpected_field": "test",
            },
        ),
        (
            "ArchiveParameters",
            ArchiveParameters,
            {
                "reason": "Processed",
                "unexpected_field": "test",
            },
        ),
        (
            "NoActionParameters",
            NoActionParameters,
            {
                "unexpected_field": "test",
            },
        ),
    ]

    for name, model, data in parameter_models:
        try:
            model.model_validate(data)
        except ValidationError:
            print(f"PASS: {name} rejects unexpected fields")
        else:
            raise AssertionError(
                f"{name} accepted an unexpected field"
            )

    print()
    print("=" * 60)
    print("PASS: All parameter schemas reject unexpected fields")


if __name__ == "__main__":
    test_extra_fields_are_rejected()