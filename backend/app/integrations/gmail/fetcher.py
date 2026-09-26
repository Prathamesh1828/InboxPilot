import logging
from typing import Any

from sqlalchemy.orm import Session

from app.integrations.gmail.client import get_gmail_service
from app.models.google_account import GoogleAccount

logger = logging.getLogger(__name__)


def _get_current_history_id(service: Any) -> str | None:
    """Get the current historyId from the user's Gmail profile."""
    try:
        profile = service.users().getProfile(userId="me").execute()
        return profile.get("historyId")
    except Exception:
        return None


def _fetch_message_ids_since_history(
    service: Any,
    start_history_id: int,
) -> list[str]:
    """
    Use the Gmail History API to find message IDs added since
    `start_history_id`. Returns a deduplicated list of message IDs.
    """
    message_ids: set[str] = set()

    try:
        response = (
            service.users()
            .history()
            .list(
                userId="me",
                startHistoryId=start_history_id,
                historyTypes=["messageAdded"],
                labelId="INBOX",
            )
            .execute()
        )

        while True:
            for history_record in response.get("history", []):
                for msg_added in history_record.get("messagesAdded", []):
                    msg = msg_added.get("message", {})
                    msg_id = msg.get("id")
                    if msg_id:
                        message_ids.add(msg_id)

            next_page = response.get("nextPageToken")
            if not next_page:
                break

            response = (
                service.users()
                .history()
                .list(
                    userId="me",
                    startHistoryId=start_history_id,
                    historyTypes=["messageAdded"],
                    labelId="INBOX",
                    pageToken=next_page,
                )
                .execute()
            )

    except Exception as exc:
        error_str = str(exc)
        # 404 means the historyId is too old / invalid — caller
        # should fall back to a full list.
        if "404" in error_str or "notFound" in error_str:
            logger.warning(
                "[GMAIL_SYNC] History ID expired, will fall back to full list"
            )
            return []
        raise

    return list(message_ids)


def _fetch_message_ids_full(
    service: Any,
    max_results: int = 25,
) -> list[str]:
    """
    Fall-back: list the most recent Inbox messages when no valid
    historyId is available.
    """
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

    return [
        m["id"]
        for m in response.get("messages", [])
        if m.get("id")
    ]


def _fetch_full_messages(
    service: Any,
    message_ids: list[str],
) -> list[dict[str, Any]]:
    """Download full message payloads for a list of message IDs."""
    results: list[dict[str, Any]] = []

    for message_id in message_ids:
        try:
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
        except Exception as exc:
            logger.warning(
                "[GMAIL_SYNC] Failed to fetch message %s: %s",
                message_id,
                type(exc).__name__,
            )

    return results


def fetch_inbox_messages(
    db: Session,
    account: GoogleAccount,
    max_results: int = 25,
) -> tuple[list[dict[str, Any]], str | None]:
    """
    Fetch new messages from the Gmail Inbox incrementally.

    Uses the History API when `account.last_history_id` is set,
    otherwise falls back to fetching the most recent messages.

    Returns:
        tuple of (messages, new_history_id)
        - messages: list of full Gmail message dicts
        - new_history_id: the historyId to save as the next checkpoint
    """

    service: Any = get_gmail_service(
        db=db,
        account=account,
    )

    # Capture the current history ID *before* fetching so we don't
    # miss anything that arrives during the fetch.
    new_history_id = _get_current_history_id(service)

    message_ids: list[str] = []
    used_history = False

    if account.last_history_id:
        message_ids = _fetch_message_ids_since_history(
            service,
            account.last_history_id,
        )
        if message_ids:
            used_history = True
            logger.info(
                "[GMAIL_SYNC] History API returned %d new message(s)",
                len(message_ids),
            )
        elif not message_ids:
            # Empty list can mean either "no new messages" (good) or
            # "historyId expired" (the function logged a warning).
            # If the historyId was valid, this is just "no new mail".
            # We still update the checkpoint below.
            if account.last_history_id:
                # Try a quick list to see if historyId was simply stale
                message_ids = _fetch_message_ids_full(
                    service, max_results=max_results
                )
                if message_ids:
                    logger.info(
                        "[GMAIL_SYNC] Fell back to full list, found %d message(s)",
                        len(message_ids),
                    )
    else:
        # First sync — no checkpoint yet.
        message_ids = _fetch_message_ids_full(
            service, max_results=max_results
        )
        logger.info(
            "[GMAIL_SYNC] Initial sync, listing %d message(s)",
            len(message_ids),
        )

    results = _fetch_full_messages(service, message_ids)

    return results, new_history_id