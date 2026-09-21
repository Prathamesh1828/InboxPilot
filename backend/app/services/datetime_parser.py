import re
from datetime import datetime, timedelta, date


# Weekday name → weekday number (Monday=0)
_WEEKDAY_MAP = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

# Month name → month number
_MONTH_MAP = {
    "january": 1, "jan": 1,
    "february": 2, "feb": 2,
    "march": 3, "mar": 3,
    "april": 4, "apr": 4,
    "may": 5,
    "june": 6, "jun": 6,
    "july": 7, "jul": 7,
    "august": 8, "aug": 8,
    "september": 9, "sep": 9, "sept": 9,
    "october": 10, "oct": 10,
    "november": 11, "nov": 11,
    "december": 12, "dec": 12,
}


def parse_calendar_datetime(
    value: str,
    reference_time: datetime,
) -> datetime:
    """
    Convert a calendar datetime string into a concrete datetime.

    Supported formats:
    - ISO datetime (2026-10-01T10:00:00)
    - today HH:MM / today at H:MM AM/PM
    - tomorrow HH:MM / tomorrow at H:MM AM/PM
    - tonight at H PM
    - Friday at 3 PM / Monday at 10:00 AM
    - October 1st / October 1 / Oct 1st
    - Bare time: "5 PM" / "3:00 PM" (resolved to today/tomorrow)
    """

    value = value.strip()

    # Already a concrete ISO datetime.
    try:
        dt = datetime.fromisoformat(value)
        if dt.tzinfo is None and reference_time is not None:
            dt = dt.replace(tzinfo=reference_time.tzinfo)
        return dt
    except ValueError:
        pass

    # ----------------------------------------------------------
    # Parse the day part and the time part separately.
    # ----------------------------------------------------------

    day_date, remaining = _parse_day_part(value, reference_time)
    hour, minute = _parse_time_part(remaining)

    return datetime(
        year=day_date.year,
        month=day_date.month,
        day=day_date.day,
        hour=hour,
        minute=minute,
        tzinfo=reference_time.tzinfo,
    )


def parse_relative_date(
    value: str,
    reference_time: datetime,
) -> date:
    """
    Parse a relative or absolute date string into a concrete date.

    Supports:
    - ISO date (2026-10-01)
    - Written dates (October 1, 2026 / Oct 1st / 1 October 2026)
    - today / tomorrow
    - Weekday names (Friday, Monday)
    - "next week" / "next month"
    """

    value = value.strip()

    # ISO date
    iso_match = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", value)
    if iso_match:
        return date(
            int(iso_match.group(1)),
            int(iso_match.group(2)),
            int(iso_match.group(3)),
        )

    value_lower = value.lower().strip().rstrip(".")

    # today / tomorrow
    if value_lower == "today":
        return reference_time.date()
    if value_lower == "tomorrow":
        return (reference_time + timedelta(days=1)).date()
    if value_lower == "tonight":
        return reference_time.date()

    # Weekday name (e.g., "Friday", "next Friday")
    clean = value_lower.replace("next ", "")
    if clean in _WEEKDAY_MAP:
        return _next_weekday(reference_time, _WEEKDAY_MAP[clean])

    # "next week" → Monday of next week
    if value_lower in ("next week",):
        days_until_monday = (7 - reference_time.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7
        return (reference_time + timedelta(days=days_until_monday)).date()

    # "next month" → 1st of next month
    if value_lower in ("next month",):
        year = reference_time.year
        month = reference_time.month + 1
        if month > 12:
            month = 1
            year += 1
        return date(year, month, 1)

    # Written dates: "October 1st", "Oct 1", "October 1, 2026", etc.
    written = _parse_written_date(value, reference_time)
    if written is not None:
        return written

    # Common date formats
    for fmt in ("%Y-%m-%d", "%B %d, %Y", "%b %d, %Y", "%d %B %Y", "%d %b %Y"):
        try:
            return datetime.strptime(value, fmt).date()
        except ValueError:
            continue

    raise ValueError(
        f"Unsupported date format: {value}"
    )


# ===========================================================
# Internal helpers
# ===========================================================

def _parse_day_part(
    value: str,
    reference_time: datetime,
) -> tuple[date, str]:
    """
    Extract the day part from a datetime string.
    Returns (resolved_date, remaining_time_string).
    """

    value_lower = value.lower().strip()

    # today / tomorrow / tonight
    for keyword, delta in [("today", 0), ("tomorrow", 1), ("tonight", 0)]:
        if value_lower.startswith(keyword):
            remaining = value_lower[len(keyword):].strip()
            # Remove optional "at"
            if remaining.startswith("at"):
                remaining = remaining[2:].strip()
            target = (reference_time + timedelta(days=delta)).date()
            return target, remaining

    # Weekday name: "Friday at 3 PM", "Monday 10:00 AM"
    for name, weekday_num in _WEEKDAY_MAP.items():
        if value_lower.startswith(name):
            remaining = value_lower[len(name):].strip()
            if remaining.startswith("at"):
                remaining = remaining[2:].strip()
            target = _next_weekday(reference_time, weekday_num)
            return target, remaining

    # Month name: "October 1st at 3 PM", "Oct 1 at 10 AM"
    written_match = re.match(
        r"([a-zA-Z]+)\s+(\d{1,2})(?:st|nd|rd|th)?"
        r"(?:,?\s*(\d{4}))?"
        r"(?:\s+(?:at\s+)?(.*))?\s*$",
        value,
        flags=re.IGNORECASE,
    )
    if written_match:
        month_str = written_match.group(1).lower()
        day_num = int(written_match.group(2))
        year_str = written_match.group(3)
        time_remaining = written_match.group(4) or ""

        if month_str in _MONTH_MAP:
            month_num = _MONTH_MAP[month_str]
            year = int(year_str) if year_str else reference_time.year
            try:
                target = date(year, month_num, day_num)
                return target, time_remaining.strip()
            except ValueError:
                pass

    # Bare time only (e.g., "5 PM", "3:00 PM") — assume today or tomorrow
    time_match = re.fullmatch(
        r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)",
        value_lower,
    )
    if time_match:
        # Return today's date; the time part is the whole value
        return reference_time.date(), value_lower

    raise ValueError(
        f"Unsupported calendar datetime format: {value}"
    )


def _parse_time_part(time_str: str) -> tuple[int, int]:
    """
    Parse the time component. Returns (hour_24, minute).

    Supports:
    - "3:00 PM", "3 PM", "15:00", "10:00 AM"
    - Empty string defaults to 09:00
    """

    time_str = time_str.strip()

    if not time_str:
        # No time given — default to 9 AM
        return 9, 0

    # HH:MM AM/PM or H:MM AM/PM
    match_12h = re.fullmatch(
        r"(\d{1,2}):(\d{2})\s*(am|pm)",
        time_str,
        flags=re.IGNORECASE,
    )
    if match_12h:
        hour = int(match_12h.group(1))
        minute = int(match_12h.group(2))
        ampm = match_12h.group(3).upper()
        hour = _convert_12h(hour, ampm)
        _validate_time(hour, minute, time_str)
        return hour, minute

    # H AM/PM (no minutes)
    match_h = re.fullmatch(
        r"(\d{1,2})\s*(am|pm)",
        time_str,
        flags=re.IGNORECASE,
    )
    if match_h:
        hour = int(match_h.group(1))
        ampm = match_h.group(2).upper()
        hour = _convert_12h(hour, ampm)
        _validate_time(hour, 0, time_str)
        return hour, 0

    # HH:MM (24-hour)
    match_24h = re.fullmatch(r"(\d{1,2}):(\d{2})", time_str)
    if match_24h:
        hour = int(match_24h.group(1))
        minute = int(match_24h.group(2))
        _validate_time(hour, minute, time_str)
        return hour, minute

    raise ValueError(
        f"Unsupported time format: {time_str}"
    )


def _convert_12h(hour: int, ampm: str) -> int:
    if ampm == "PM" and hour < 12:
        hour += 12
    elif ampm == "AM" and hour == 12:
        hour = 0
    return hour


def _validate_time(hour: int, minute: int, original: str) -> None:
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        raise ValueError(f"Invalid time: {original}")


def _next_weekday(
    reference_time: datetime,
    target_weekday: int,
) -> date:
    """Return the next occurrence of a weekday from reference_time."""
    current_weekday = reference_time.weekday()
    days_ahead = target_weekday - current_weekday
    if days_ahead <= 0:
        days_ahead += 7
    return (reference_time + timedelta(days=days_ahead)).date()


def _parse_written_date(
    value: str,
    reference_time: datetime,
) -> date | None:
    """Try to parse written date formats like 'October 1st', 'Oct 1'."""

    # "October 1st", "Oct 1, 2026"
    match = re.fullmatch(
        r"([a-zA-Z]+)\s+(\d{1,2})(?:st|nd|rd|th)?(?:,?\s*(\d{4}))?",
        value.strip(),
    )
    if match:
        month_str = match.group(1).lower()
        day = int(match.group(2))
        year_str = match.group(3)

        if month_str in _MONTH_MAP:
            month = _MONTH_MAP[month_str]
            year = int(year_str) if year_str else reference_time.year
            try:
                return date(year, month, day)
            except ValueError:
                pass

    # "1 October 2026", "1 Oct"
    match2 = re.fullmatch(
        r"(\d{1,2})\s+([a-zA-Z]+)(?:\s+(\d{4}))?",
        value.strip(),
    )
    if match2:
        day = int(match2.group(1))
        month_str = match2.group(2).lower()
        year_str = match2.group(3)

        if month_str in _MONTH_MAP:
            month = _MONTH_MAP[month_str]
            year = int(year_str) if year_str else reference_time.year
            try:
                return date(year, month, day)
            except ValueError:
                pass

    return None