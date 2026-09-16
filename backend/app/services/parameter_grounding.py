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

    # -------------------------------------------------
    # CREATE_CALENDAR_EVENT
    # -------------------------------------------------

    elif plan.action == ActionType.CREATE_CALENDAR_EVENT:
        parameters = plan.parameters

        # Validate event title.
        if not parameters.title:
            errors.append(
                "Calendar event title is missing from action parameters."
            )
        elif not _calendar_title_is_grounded(
            title=parameters.title,
            email_text=email_text,
        ):
            errors.append(
                f"Calendar event title '{parameters.title}' "
                "was not sufficiently grounded in the email."
            )

        # Start time is required.
        if parameters.start_time is None:
            errors.append(
                "Calendar event start time is missing from action parameters."
            )
        elif not _datetime_is_grounded(
            value=parameters.start_time,
            body=body,
        ):
            errors.append(
                f"Calendar event start time '{parameters.start_time}' "
                "was not clearly found in email body."
            )

        # End time is optional.
        if parameters.end_time is not None:
            if not _datetime_is_grounded(
                value=parameters.end_time,
                body=body,
            ):
                errors.append(
                    f"Calendar event end time '{parameters.end_time}' "
                    "was not clearly found in email body."
                )

        # Description is optional.
        if parameters.description is not None:
            if not _description_is_grounded(
                description=parameters.description,
                email_text=email_text,
            ):
                errors.append(
                    "Calendar event description was not sufficiently "
                    "grounded in the email."
                )

    # -------------------------------------------------
    # DRAFT_REPLY
    # -------------------------------------------------

    elif plan.action == ActionType.DRAFT_REPLY:
        parameters = plan.parameters

        if not parameters.reply_text:
            errors.append(
                "Draft reply text is missing from action parameters."
            )
        elif not _reply_is_grounded(
            reply_text=parameters.reply_text,
            email_text=email_text,
        ):
            errors.append(
                "Draft reply was not sufficiently grounded "
                "in the original email."
            )

    return errors


# =====================================================
# BILL HELPERS
# =====================================================

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


# =====================================================
# REMINDER HELPERS
# =====================================================

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


# =====================================================
# CALENDAR HELPERS
# =====================================================

def _calendar_title_is_grounded(
    title: str,
    email_text: str,
) -> bool:
    """
    Check whether the calendar event title is sufficiently
    supported by words found in the email.

    Example:

    Email:
        Meeting with the client about the new project.

    Title:
        Client project meeting

    This passes because the meaningful words overlap.
    """

    title_words = _meaningful_words(title)
    email_words = _meaningful_words(email_text)

    if not title_words:
        return False

    matched_words = title_words.intersection(email_words)

    match_ratio = len(matched_words) / len(title_words)

    return match_ratio >= 0.5


def _datetime_is_grounded(
    value: str,
    body: str,
) -> bool:
    """
    Check whether a calendar datetime is supported by
    information present in the email body.

    Supports:

    2026-09-20T10:00
    2026-09-20 10:00
    today 10:00
    tomorrow 10:00

    The function requires the relevant date and time
    information to appear in the email.
    """

    value = value.strip()

    if not value:
        return False

    body_lower = body.lower()

    # -------------------------------------------------
    # Exact match
    # -------------------------------------------------

    if value.lower() in body_lower:
        return True

    # -------------------------------------------------
    # ISO datetime
    # -------------------------------------------------

    iso_match = re.fullmatch(
        r"(\d{4})-(\d{2})-(\d{2})[T ]"
        r"(\d{2}):(\d{2})(?::\d{2})?",
        value,
    )

    if iso_match:
        year, month, day, hour, minute = (
            iso_match.group(1),
            iso_match.group(2),
            iso_match.group(3),
            iso_match.group(4),
            iso_match.group(5),
        )

        # Validate that the date is actually valid.
        try:
            parsed_date = date(
                int(year),
                int(month),
                int(day),
            )
        except ValueError:
            return False

        # Support common date representations.
        date_formats = [
            f"{year}-{month}-{day}",
            f"{month}/{day}/{year}",
            f"{month}-{day}-{year}",
            f"{parsed_date.strftime('%B')} "
            f"{parsed_date.day}, {year}",
            f"{parsed_date.strftime('%b')} "
            f"{parsed_date.day}, {year}",
            f"{parsed_date.day} "
            f"{parsed_date.strftime('%B')} {year}",
            f"{parsed_date.day} "
            f"{parsed_date.strftime('%b')} {year}",
        ]

        # Support zero-padded and non-zero-padded times.
        hour_int = int(hour)
        minute_int = int(minute)

        time_formats = [
            f"{hour}:{minute}",
            f"{hour_int}:{minute_int:02d}",
        ]

        date_found = any(
            date_value.lower() in body_lower
            for date_value in date_formats
        )

        time_found = any(
            time_value.lower() in body_lower
            for time_value in time_formats
        )

        return date_found and time_found

    # -------------------------------------------------
    # today / tomorrow datetime
    # -------------------------------------------------

    parts = value.split()

    if len(parts) == 2:
        day_keyword, time_value = parts

        if day_keyword.lower() in {"today", "tomorrow"}:
            if re.fullmatch(
                r"\d{1,2}:\d{2}",
                time_value,
            ):
                return (
                    day_keyword.lower() in body_lower
                    and time_value in body_lower
                )

    return False


def _description_is_grounded(
    description: str,
    email_text: str,
) -> bool:
    """
    Check whether the calendar description contains
    enough meaningful information from the email.
    """

    description_words = _meaningful_words(description)
    email_words = _meaningful_words(email_text)

    if not description_words:
        return False

    matched_words = description_words.intersection(email_words)

    match_ratio = len(matched_words) / len(description_words)

    return match_ratio >= 0.5


# =====================================================
# DRAFT REPLY HELPERS
# =====================================================

def _reply_is_grounded(
    reply_text: str,
    email_text: str,
) -> bool:
    """
    Check whether a generated reply contains enough
    meaningful words from the original email.

    This does NOT require the reply to copy the email.

    It is only intended as a safety check against a reply
    that is completely unrelated to the original message.
    """

    reply_words = _meaningful_words(reply_text)
    email_words = _meaningful_words(email_text)

    if not reply_words:
        return False

    matched_words = reply_words.intersection(email_words)

    match_ratio = len(matched_words) / len(reply_words)

    return match_ratio >= 0.3


# =====================================================
# COMMON TEXT HELPERS
# =====================================================

def _meaningful_words(text: str) -> set[str]:
    """
    Extract meaningful words while ignoring common stop words.
    """

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


# =====================================================
# DATE HELPERS
# =====================================================

def _date_is_grounded(
    due_date: str,
    body: str,
) -> bool:
    """
    Check whether a YYYY-MM-DD date is represented
    somewhere in the email body.

    Supports:

    2026-09-20
    September 20, 2026
    Sep 20, 2026
    20 September 2026
    20 Sep 2026
    """

    if due_date in body:
        return True

    match = re.fullmatch(
        r"(\d{4})-(\d{2})-(\d{2})",
        due_date,
    )

    if not match:
        return False

    year, month, day = map(
        int,
        match.groups(),
    )

    try:
        parsed_date = date(
            year,
            month,
            day,
        )
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