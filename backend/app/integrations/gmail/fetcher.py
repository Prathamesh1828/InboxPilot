from typing import Any

from sqlalchemy.orm import Session

from app.integrations.gmail.client import get_gmail_service
from app.models.google_account import GoogleAccount


def fetch_inbox_messages(
    db: Session,
    account: GoogleAccount,
    max_results: int = 10,
) -> list[dict[str, Any]]:
    """
    Fetch messages from the Gmail Inbox.

    This function only communicates with Gmail.
    It does not save anything to the database yet.
    """

    service: Any = get_gmail_service(
        db=db,
        account=account,
    )

    response = (
        service.users()
        .messages()
        .list(
            userId="me",
            labelIds=["INBOX"],
            maxResults=max_results,
        )
        .execute()
    )

    messages = response.get("messages", [])

    results: list[dict[str, Any]] = []

    for message in messages:
        message_id = message.get("id")

        if not message_id:
            continue

        full_message = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=message_id,
                format="full",
            )
            .execute()
        )

        results.append(full_message)

    return results