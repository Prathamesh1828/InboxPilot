import re
from datetime import date
from decimal import Decimal, InvalidOperation

from app.schemas.action_plan import (
    ActionPlan,
    ActionType,
)


def validate_action_parameters(
    plan: ActionPlan,
    subject: str | None,
    body: str,
) -> list[str]:
    """
    Check whether action parameters are present and
    grounded in the original email.

    Returns a list of grounding errors.
    An empty list means the parameters passed validation.
    """

    errors: list[str] = []

    email_text = " ".join(
        part
        for part in [subject, body]
        if part
    )

    # -------------------------------------------------
    # LOG_BILL
    # -------------------------------------------------

    if plan.action == ActionType.LOG_BILL:
        parameters = plan.parameters

        if not _amount_is_grounded(
            amount=parameters.amount,
            body=body,
        ):
            errors.append(
                f"Bill amount '{parameters.amount}' "
                "was not found in email body."
            )

        if not parameters.currency:
            errors.append(
                "Bill currency is missing from action parameters."
            )

        if parameters.due_date is not None:
            if not _date_is_grounded(
                due_date=parameters.due_date,
                body=body,
            ):
                errors.append(
                    f"Due date '{parameters.due_date}' was not clearly "
                    "found in email body."
                )

        if parameters.vendor is not None:
            if parameters.vendor.lower() not in body.lower():
                errors.append(
                    f"Vendor '{parameters.vendor}' was not found "
                    "in email body."
                )

    # -------------------------------------------------
    # CREATE_REMINDER
    # -------------------------------------------------

    elif plan.action == ActionType.CREATE_REMINDER:
        parameters = plan.parameters

        if not parameters.reminder_text:
            errors.append(
                "Reminder text is missing from action parameters."
            )
        elif not _reminder_text_is_grounded(
            reminder_text=parameters.reminder_text,
            email_text=email_text,
        ):
            errors.append(
                f"Reminder text '{parameters.reminder_text}' "
                "was not sufficiently grounded in the email."
            )

        if parameters.reminder_date is None:
            errors.append(
                "Reminder date is missing from action parameters."
            )
        elif not _date_is_grounded(
            due_date=parameters.reminder_date,
            body=body,
        ):
            errors.append(
                f"Reminder date '{parameters.reminder_date}' "
                "was not clearly found in email body."
            )

    return errors


def _amount_is_grounded(
    amount: float,
    body: str,
) -> bool:
    """
    Check whether a numeric bill amount appears in the email.

    Handles equivalent representations such as:
    2450
    2450.0
    ₹2450
    INR 2450

    It avoids substring false positives such as treating
    2450 as present inside 24500.
    """

    try:
        expected_amount = Decimal(str(amount))
    except (InvalidOperation, ValueError):
        return False

    amount_matches = re.findall(
        r"(?<![\d.])\d+(?:,\d{3})*(?:\.\d+)?"
        r"(?=$|[^\d.]|[.](?!\d))",
        body,
    )

    for match in amount_matches:
        normalized_match = match.replace(",", "")

        try:
            email_amount = Decimal(normalized_match)
        except InvalidOperation:
            continue

        if email_amount == expected_amount:
            return True

    return False


def _reminder_text_is_grounded(
    reminder_text: str,
    email_text: str,
) -> bool:
    reminder_words = _meaningful_words(reminder_text)
    email_words = _meaningful_words(email_text)

    if not reminder_words:
        return False

    matched_words = reminder_words.intersection(email_words)
    match_ratio = len(matched_words) / len(reminder_words)

    return match_ratio >= 0.5


def _meaningful_words(text: str) -> set[str]:
    stop_words = {
        "a",
        "an",
        "and",
        "are",
        "as",
        "at",
        "be",
        "by",
        "for",
        "from",
        "in",
        "is",
        "it",
        "of",
        "on",
        "or",
        "the",
        "to",
        "your",
    }

    words = re.findall(
        r"[a-zA-Z0-9]+",
        text.lower(),
    )

    return {
        word
        for word in words
        if word not in stop_words
    }


def _date_is_grounded(
    due_date: str,
    body: str,
) -> bool:
    if due_date in body:
        return True

    match = re.fullmatch(
        r"(\d{4})-(\d{2})-(\d{2})",
        due_date,
    )

    if not match:
        return False

    year, month, day = map(int, match.groups())

    try:
        parsed_date = date(year, month, day)
    except ValueError:
        return False

    month_name = parsed_date.strftime("%B")
    month_short = parsed_date.strftime("%b")

    readable_formats = [
        f"{month_name} {day}, {year}",
        f"{month_short} {day}, {year}",
        f"{day} {month_name} {year}",
        f"{day} {month_short} {year}",
    ]

    body_lower = body.lower()

    return any(
        readable_date.lower() in body_lower
        for readable_date in readable_formats
    )