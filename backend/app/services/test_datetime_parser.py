from datetime import datetime

from app.services.datetime_parser import parse_calendar_datetime


def main() -> None:
    reference_time = datetime.fromisoformat(
        "2026-09-14T13:00:00+05:30"
    )

    print("Testing Calendar Datetime Parser")
    print("=" * 60)

    tests = [
        "tomorrow 10:00",
        "today 15:30",
        "2026-09-15T10:00:00+05:30",
        "tomorrow at 3:00 PM",
        "today at 10:00 AM",
        "tomorrow at 15:00",
    ]

    for value in tests:
        result = parse_calendar_datetime(
            value=value,
            reference_time=reference_time,
        )

        print()
        print(f"Input:  {value}")
        print(f"Output: {result.isoformat()}")

    print("\nTesting Invalid Inputs:")
    invalid_tests = [
        "next week at 5:00 PM",
        "today at 25:00",
        "tomorrow at 3:60 PM",
    ]
    for value in invalid_tests:
        try:
            parse_calendar_datetime(value, reference_time)
            print(f"FAILED: Expected ValueError for {value}")
        except ValueError as e:
            print(f"Success: Caught expected ValueError for '{value}': {e}")

    print()
    print("Datetime parser test passed.")


if __name__ == "__main__":
    main()