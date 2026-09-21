from datetime import datetime, date, timezone
import pytest

from app.services.datetime_parser import (
    parse_calendar_datetime,
    parse_relative_date,
)

def test_parse_calendar_datetime():
    reference_time = datetime(2026, 9, 21, 10, 0, tzinfo=timezone.utc)
    
    # ISO date
    dt = parse_calendar_datetime("2026-10-01T15:30:00", reference_time)
    assert dt == datetime(2026, 10, 1, 15, 30, tzinfo=timezone.utc)
    
    # Today / Tomorrow
    dt = parse_calendar_datetime("tomorrow 10:00", reference_time)
    assert dt == datetime(2026, 9, 22, 10, 0, tzinfo=timezone.utc)
    
    dt = parse_calendar_datetime("today at 3 PM", reference_time)
    assert dt == datetime(2026, 9, 21, 15, 0, tzinfo=timezone.utc)
    
    # Tonight
    dt = parse_calendar_datetime("tonight at 8 PM", reference_time)
    assert dt == datetime(2026, 9, 21, 20, 0, tzinfo=timezone.utc)
    
    # Weekday (2026-09-21 is Monday)
    dt = parse_calendar_datetime("Friday at 5:00 PM", reference_time)
    assert dt == datetime(2026, 9, 25, 17, 0, tzinfo=timezone.utc)
    
    # Next week
    dt = parse_calendar_datetime("Monday 10 AM", reference_time) # Same day or next week? The logic goes 7 days ahead if today is Monday and we ask for Monday
    assert dt == datetime(2026, 9, 28, 10, 0, tzinfo=timezone.utc)
    
    # Bare time
    dt = parse_calendar_datetime("5 PM", reference_time)
    assert dt == datetime(2026, 9, 21, 17, 0, tzinfo=timezone.utc)
    
    # Written date
    dt = parse_calendar_datetime("October 1st at 10 AM", reference_time)
    assert dt == datetime(2026, 10, 1, 10, 0, tzinfo=timezone.utc)

def test_parse_relative_date():
    reference_time = datetime(2026, 9, 21, 10, 0, tzinfo=timezone.utc)
    
    assert parse_relative_date("today", reference_time) == date(2026, 9, 21)
    assert parse_relative_date("tomorrow", reference_time) == date(2026, 9, 22)
    assert parse_relative_date("Friday", reference_time) == date(2026, 9, 25)
    
    # "next week" -> Monday of next week
    assert parse_relative_date("next week", reference_time) == date(2026, 9, 28)
    
    # "next month" -> 1st of next month
    assert parse_relative_date("next month", reference_time) == date(2026, 10, 1)
    
    # ISO
    assert parse_relative_date("2026-10-01", reference_time) == date(2026, 10, 1)
    
    # Written
    assert parse_relative_date("October 1st", reference_time) == date(2026, 10, 1)
    assert parse_relative_date("Oct 1, 2026", reference_time) == date(2026, 10, 1)
    assert parse_relative_date("1 October 2026", reference_time) == date(2026, 10, 1)

def test_invalid_dates():
    reference_time = datetime(2026, 9, 21, 10, 0, tzinfo=timezone.utc)
    
    with pytest.raises(ValueError):
        parse_calendar_datetime("invalid format", reference_time)
        
    with pytest.raises(ValueError):
        parse_relative_date("invalid date", reference_time)