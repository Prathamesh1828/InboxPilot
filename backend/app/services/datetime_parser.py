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
    """

    value = value.strip()

    # Already a concrete ISO datetime.
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        pass

    parts = value.split()

    if len(parts) != 2:
        raise ValueError(
            f"Unsupported calendar datetime format: {value}"
        )

    day_keyword, time_value = parts

    try:
        hour, minute = map(int, time_value.split(":"))
    except ValueError as exc:
        raise ValueError(
            f"Invalid calendar time: {value}"
        ) from exc

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