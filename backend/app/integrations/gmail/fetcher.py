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
) -> list[str] | None:
    """
    Use the Gmail History API to find message IDs added since
    `start_history_id`. Returns a deduplicated list of message IDs.

    Returns:
        list[str]  — message IDs of new messages (may be empty if
                     no new mail has arrived since the checkpoint).
        None       — the stored historyId is expired/invalid and the
                     caller should fall back to a full message list.
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
            return None
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
    Fetch new messages from Gmail incrementally.

    Uses the History API when `account.last_history_id` is set,
    otherwise falls back to fetching the most recent messages.

    The History API query does NOT filter by label so that messages
    arriving in SPAM, Promotions, or other tabs are also captured.
    Only the initial full-list fallback is scoped to INBOX.

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

    if account.last_history_id:
        result = _fetch_message_ids_since_history(
            service,
            int(account.last_history_id),
        )

        if result is None:
            # historyId expired — fall back to full message list.
            message_ids = _fetch_message_ids_full(
                service, max_results=max_results
            )
            logger.info(
                "[GMAIL_SYNC] Fell back to full list, found %d message(s)",
                len(message_ids),
            )
        elif result:
            message_ids = result
            logger.info(
                "[GMAIL_SYNC] History API returned %d new message(s)",
                len(message_ids),
            )
        else:
            # Empty list = genuinely no new messages since the last
            # checkpoint.  This is the normal steady-state path.
            logger.info("[GMAIL_SYNC] No new messages since last sync")
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