import re
from datetime import datetime, timedelta


def parse_calendar_datetime(
    value: str,
    reference_time: datetime,
) -> datetime:
    """
    Convert a calendar datetime string into a concrete datetime.

    Supported formats:
    - ISO datetime
    - tomorrow HH:MM
    - today HH:MM
    - tomorrow at 3:00 PM
    - today at 10:00 AM
    - tomorrow at 15:00
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

    pattern = r"^(today|tomorrow)(?:\s+at)?\s+(\d{1,2}):(\d{2})(?:\s+(AM|PM|am|pm))?$"
    match = re.match(pattern, value, flags=re.IGNORECASE)

    if not match:
        raise ValueError(
            f"Unsupported calendar datetime format: {value}"
        )

    day_keyword, hour_str, minute_str, ampm = match.groups()
    hour = int(hour_str)
    minute = int(minute_str)

    if ampm:
        ampm = ampm.upper()
        if ampm == "PM" and hour < 12:
            hour += 12
        elif ampm == "AM" and hour == 12:
            hour = 0

    if not 0 <= hour <= 23 or not 0 <= minute <= 59:
        raise ValueError(
            f"Invalid calendar time: {value}"
        )

    if day_keyword.lower() == "today":
        target_date = reference_time.date()
    elif day_keyword.lower() == "tomorrow":
        target_date = (
            reference_time + timedelta(days=1)
        ).date()
    else:
        raise ValueError(
            f"Unsupported calendar date keyword: {day_keyword}"
        )

    return datetime(
        year=target_date.year,
        month=target_date.month,
        day=target_date.day,
        hour=hour,
        minute=minute,
        tzinfo=reference_time.tzinfo,
    )