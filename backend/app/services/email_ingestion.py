import json
import logging

from typing import cast

from sqlalchemy.orm import Session

from app.integrations.gmail.fetcher import fetch_inbox_messages
from app.integrations.gmail.parser import parse_gmail_message
from app.models.google_account import GoogleAccount
from app.repositories.email_repository import create_email_if_not_exists

logger = logging.getLogger(__name__)


def _publish_new_email_event(db: Session, email) -> None:
    """Publish an SSE event so the frontend can auto-refresh."""
    try:
        from app.core.redis import redis_client

        if email.user_id:
            event = {
                "type": "EMAIL_INGESTED",
                "email_id": email.id,
                "status": email.status,
            }
            redis_client.publish(
                f"inbox_events:{email.user_id}",
                json.dumps(event),
            )
    except Exception as exc:
        logger.debug(
            "[GMAIL_SYNC] Failed to publish new-email event: %s",
            type(exc).__name__,
        )


def ingest_inbox_emails(
    db: Session,
    account: GoogleAccount,
    max_results: int = 25,
    import_only: bool = False,
) -> dict[str, int]:
    """
    Fetch Inbox messages from Gmail, parse them, store new messages
    in the database, and optionally queue newly inserted emails for
    background processing.

    When ``import_only`` is True the emails are stored with the status
    ``IMPORTED`` and are **not** sent to the AI processing pipeline.
    This is used for the initial fetch after connecting a Gmail account
    so that historical emails populate the inbox without triggering
    automated actions on stale threads.

    Existing messages are skipped using the Gmail provider message ID.

    The function updates the account's ``last_history_id`` checkpoint
    on success so subsequent polls only fetch new messages.
    """

    messages, new_history_id = fetch_inbox_messages(
        db=db,
        account=account,
        max_results=max_results,
    )

    inserted = 0
    skipped = 0
    failed = 0
    processing_queued = 0

    for message in messages:
        try:
            parsed_email = parse_gmail_message(message)

            email, created = create_email_if_not_exists(
                db=db,
                provider_message_id=parsed_email[
                    "provider_message_id"
                ],
                thread_id=parsed_email["thread_id"],
                sender=parsed_email["sender"],
                recipients=parsed_email["recipients"],
                subject=parsed_email["subject"],
                body=parsed_email["body"],
                received_at=parsed_email["received_at"],
                user_id=cast(str | None, account.user_id),
            )

            if created:
                inserted += 1

                if import_only:
                    # Mark as imported — visible in the inbox but
                    # will NOT be processed by the AI pipeline.
                    email.status = "IMPORTED"
                    db.commit()

                    logger.info(
                        "[GMAIL_SYNC] Email imported (no processing): id=%d",
                        email.id,
                    )
                else:
                    logger.info(
                        "[GMAIL_SYNC] New email ingested: id=%d",
                        email.id,
                    )

                    # Lazy import to avoid circular dependency
                    from app.workers.tasks import process_email_pipeline

                    # Send the newly created email to Celery.
                    task = process_email_pipeline.delay(email.id)
                    processing_queued += 1

                    logger.info(
                        "[GMAIL_SYNC] Processing task queued: email=%d task=%s",
                        email.id,
                        task.id,
                    )

                # Notify frontend via SSE
                _publish_new_email_event(db, email)

            else:
                skipped += 1

        except Exception as e:
            failed += 1

            logger.error(
                "[GMAIL_SYNC] Failed to ingest Gmail message: %s: %s",
                type(e).__name__,
                e,
            )

    # ---------------------------------------------------------
    # Update the sync checkpoint so the next poll is incremental.
    # ---------------------------------------------------------
    if new_history_id is not None:
        try:
            account.last_history_id = int(new_history_id)
            db.commit()
            db.refresh(account)
            logger.info(
                "[GMAIL_SYNC] Checkpoint updated: history_id=%s",
                new_history_id,
            )
        except Exception as exc:
            logger.error(
                "[GMAIL_SYNC] Failed to update checkpoint: %s",
                type(exc).__name__,
            )

    return {
        "fetched": len(messages),
        "inserted": inserted,
        "skipped": skipped,
        "failed": failed,
        "processing_queued": processing_queued,
    }