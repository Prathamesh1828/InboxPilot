from datetime import datetime
from typing import Any

from googleapiclient.discovery import build
from sqlalchemy.orm import Session

from app.integrations.gmail.client import get_google_credentials
from app.models.google_account import GoogleAccount


def get_calendar_service(
    db: Session,
    account: GoogleAccount,
) -> Any:
    """
    Build and return an authenticated Google Calendar API service.
    """

    credentials = get_google_credentials(
        db=db,
        account=account,
    )

    return build(
        "calendar",
        "v3",
        credentials=credentials,
    )


def create_calendar_event(
    db: Session,
    account: GoogleAccount,
    title: str,
    start_time: datetime,
    end_time: datetime,
    description: str | None = None,
) -> str:
    """
    Create an event in the user's primary Google Calendar.

    Returns the Google Calendar event ID.
    """

    service = get_calendar_service(
        db=db,
        account=account,
    )

    event_body = {
        "summary": title,
        "description": description,
        "start": {
            "dateTime": start_time.isoformat(),
        },
        "end": {
            "dateTime": end_time.isoformat(),
        },
    }

    try:
        created_event = (
            service.events()
            .insert(
                calendarId="primary",
                body=event_body,
            )
            .execute()
        )
    except Exception as exc:
        raise RuntimeError(
            f"Google Calendar API error while creating event: {exc}"
        ) from exc

    return created_event["id"]