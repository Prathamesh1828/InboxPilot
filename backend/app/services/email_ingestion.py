import logging

from typing import cast

from sqlalchemy.orm import Session

from app.integrations.gmail.fetcher import fetch_inbox_messages
from app.integrations.gmail.parser import parse_gmail_message
from app.models.google_account import GoogleAccount
from app.repositories.email_repository import create_email_if_not_exists
from app.workers.tasks import process_email_pipeline

logger = logging.getLogger(__name__)


def ingest_inbox_emails(
    db: Session,
    account: GoogleAccount,
    max_results: int = 10,
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
    """

    messages = fetch_inbox_messages(
        db=db,
        account=account,
        max_results=max_results,
    )

    inserted = 0
    skipped = 0
    failed = 0

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
                        "Email imported (no processing): id=%d",
                        email.id,
                    )
                else:
                    logger.info(
                        "New email ingested: id=%d",
                        email.id,
                    )

                    # Send the newly created email to Celery.
                    task = process_email_pipeline.delay(email.id)

                    logger.info(
                        "Celery task queued: email=%d task=%s",
                        email.id,
                        task.id,
                    )

            else:
                skipped += 1

                logger.debug(
                    "Email already exists: id=%d",
                    email.id,
                )

        except Exception as e:
            failed += 1

            logger.error(
                "Failed to ingest Gmail message %s: %s: %s",
                message.get("id"),
                type(e).__name__,
                e,
            )

    return {
        "fetched": len(messages),
        "inserted": inserted,
        "skipped": skipped,
        "failed": failed,
    }