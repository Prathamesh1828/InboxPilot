import re
from datetime import date, datetime, timedelta
from decimal import Decimal, InvalidOperation

from app.schemas.action_plan import (
    ActionPlan,
    ActionType,
)


def validate_action_parameters(
    plan: ActionPlan,
    subject: str | None,
    body: str,
    reference_time: datetime | None = None,
) -> list[str]:
    """
    Check whether action parameters are present and
    grounded in the original email.

    reference_time is normally the email's received_at
    timestamp. It allows relative expressions such as
    "today" and "tomorrow" to be compared against
    normalized planner output.

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
                reference_time=reference_time,
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
            reference_time=reference_time,
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
            reference_time=reference_time,
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
                reference_time=reference_time,
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
    reference_time: datetime | None = None,
) -> bool:
    """
    Check whether a normalized calendar datetime is supported
    by information present in the email body.

    Supports:

    2026-09-20T10:00
    2026-09-20 10:00
    today 10:00
    tomorrow 10:00

    Also understands planner normalization such as:

    Email:
        tomorrow at 3:00 PM

    Planner:
        2026-09-18T15:00:00

    when reference_time is 2026-09-17.
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
        r"(\d{2}):(\d{2})(?::(\d{2}))?",
        value,
    )

    if iso_match:
        year = int(iso_match.group(1))
        month = int(iso_match.group(2))
        day = int(iso_match.group(3))
        hour = int(iso_match.group(4))
        minute = int(iso_match.group(5))

        try:
            parsed_datetime = datetime(
                year=year,
                month=month,
                day=day,
                hour=hour,
                minute=minute,
                tzinfo=(
                    reference_time.tzinfo
                    if reference_time is not None
                    else None
                ),
            )
        except ValueError:
            return False

        # -------------------------------------------------
        # Relative date normalization
        # -------------------------------------------------

        if reference_time is not None:
            relative_dates = {
                "today": reference_time.date(),
                "tonight": reference_time.date(),
                "tomorrow": (
                    reference_time + timedelta(days=1)
                ).date(),
            }

            for keyword, expected_date in relative_dates.items():
                if parsed_datetime.date() != expected_date:
                    continue

                # The email must actually mention the
                # relative day keyword.
                if keyword not in body_lower:
                    continue

                # Check that the email contains the
                # corresponding time.
                if _time_is_grounded(
                    hour=hour,
                    minute=minute,
                    body=body,
                ):
                    return True

            weekday_name = parsed_datetime.strftime("%A").lower()
            if weekday_name in body_lower:
                if _time_is_grounded(hour=hour, minute=minute, body=body):
                    return True

        # -------------------------------------------------
        # Absolute date representation
        # -------------------------------------------------

        date_formats = [
            f"{year:04d}-{month:02d}-{day:02d}",
            f"{month}/{day}/{year}",
            f"{month}-{day}-{year}",
            f"{parsed_datetime.strftime('%B')} "
            f"{parsed_datetime.day}, {year}",
            f"{parsed_datetime.strftime('%b')} "
            f"{parsed_datetime.day}, {year}",
            f"{parsed_datetime.day} "
            f"{parsed_datetime.strftime('%B')} {year}",
            f"{parsed_datetime.day} "
            f"{parsed_datetime.strftime('%b')} {year}",
        ]

        date_found = any(
            date_value.lower() in body_lower
            for date_value in date_formats
        )

        time_found = _time_is_grounded(
            hour=hour,
            minute=minute,
            body=body,
        )

        return date_found and time_found

    # -------------------------------------------------
    # today / tomorrow datetime
    # -------------------------------------------------

    parts = value.split()

    if len(parts) == 2:
        day_keyword, time_value = parts

        if day_keyword.lower() in {
            "today",
            "tonight",
            "tomorrow",
        }:
            if re.fullmatch(
                r"\d{1,2}:\d{2}",
                time_value,
            ):
                return (
                    day_keyword.lower() in body_lower
                    and time_value in body_lower
                )

    return False


def _time_is_grounded(
    hour: int,
    minute: int,
    body: str,
) -> bool:
    """
    Check whether the specified time appears in the email.

    Supports:

    15:00
    3:00 PM
    03:00 PM
    3 PM
    15.00
    """

    body_lower = body.lower()

    # 24-hour formats.
    twenty_four_hour_formats = {
        f"{hour}:{minute:02d}",
        f"{hour:02d}:{minute:02d}",
        f"{hour}.{minute:02d}",
        f"{hour:02d}.{minute:02d}",
    }

    if any(
        time_value in body_lower
        for time_value in twenty_four_hour_formats
    ):
        return True

    # 12-hour format.
    period = "am" if hour < 12 else "pm"

    hour_12 = hour % 12

    if hour_12 == 0:
        hour_12 = 12

    twelve_hour_formats = {
        f"{hour_12}:{minute:02d} {period}",
        f"{hour_12}:{minute:02d}{period}",
        f"{hour_12} {period}",
        f"{hour_12}{period}",
    }

    return any(
        time_value in body_lower
        for time_value in twelve_hour_formats
    )


def _description_is_grounded(
    description: str,
    email_text: str,
) -> bool:
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
    reply_words = _meaningful_words(reply_text)
    email_words = _meaningful_words(email_text)

    if not reply_words:
        return False

    matched_words = reply_words.intersection(email_words)

    match_ratio = len(matched_words) / len(reply_words)

    return match_ratio >= 0.15


# =====================================================
# COMMON TEXT HELPERS
# =====================================================

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


# =====================================================
# DATE HELPERS
# =====================================================

def _date_is_grounded(
    due_date: str,
    body: str,
    reference_time: datetime | None = None,
) -> bool:
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

    body_lower = body.lower()

    if reference_time is not None:
        relative_dates = {
            "today": reference_time.date(),
            "tonight": reference_time.date(),
            "tomorrow": (reference_time + timedelta(days=1)).date(),
        }
        for keyword, expected_date in relative_dates.items():
            if parsed_date == expected_date and keyword in body_lower:
                return True
                
        weekday_name = parsed_date.strftime("%A").lower()
        if weekday_name in body_lower:
            return True

    month_name = parsed_date.strftime("%B")
    month_short = parsed_date.strftime("%b")

    readable_formats = [
        f"{month_name} {day}, {year}",
        f"{month_short} {day}, {year}",
        f"{day} {month_name} {year}",
        f"{day} {month_short} {year}",
        f"{month_name} {day}",
        f"{month_short} {day}",
        f"{month_name} {day}st",
        f"{month_name} {day}nd",
        f"{month_name} {day}rd",
        f"{month_name} {day}th",
    ]

    return any(
        readable_date.lower() in body_lower
        for readable_date in readable_formats
    )