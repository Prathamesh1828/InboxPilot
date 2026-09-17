from sqlalchemy.orm import Session

from app.integrations.gmail.fetcher import fetch_inbox_messages
from app.integrations.gmail.parser import parse_gmail_message
from app.models.google_account import GoogleAccount
from app.repositories.email_repository import create_email_if_not_exists
from app.workers.tasks import process_email_pipeline


def ingest_inbox_emails(
    db: Session,
    account: GoogleAccount,
    max_results: int = 10,
) -> dict[str, int]:
    """
    Fetch Inbox messages from Gmail, parse them, store new messages
    in the database, and queue newly inserted emails for background
    processing.

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
            )

            if created:
                inserted += 1

                print(
                    f"[Ingestion] New email created: "
                    f"{email.id}"
                )

                # Send the newly created email to Celery.
                task = process_email_pipeline.delay(email.id)

                print(
                    f"[Ingestion] Celery task queued: "
                    f"{task.id}"
                )

            else:
                skipped += 1

                print(
                    f"[Ingestion] Email already exists: "
                    f"{email.id}"
                )

        except Exception as e:
            failed += 1

            print(
                "❌ Failed to ingest Gmail message "
                f"{message.get('id')}: "
                f"{type(e).__name__}: {e}"
            )

    return {
        "fetched": len(messages),
        "inserted": inserted,
        "skipped": skipped,
        "failed": failed,
    }