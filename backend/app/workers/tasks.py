import logging

from celery import Task

from app.db.database import SessionLocal
from app.repositories.email_repository import get_email_by_id
from app.services.email_pipeline import EmailPipeline
from app.services.workflow_service import WorkflowService
from app.workers.celery_app import celery_app
from app.models.google_account import GoogleAccount

logger = logging.getLogger(__name__)


class DatabaseTask(Task):
    """Base Celery task that provides database-session handling."""


# ---------------------------------------------------------
# Terminal statuses — emails in these states must not
# be processed again.
# ---------------------------------------------------------

_TERMINAL_STATUSES = {
    "COMPLETED",
    "APPROVAL_PENDING",
    "GROUNDING_REVIEW",
    "EXECUTED",
}


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.workers.tasks.process_email",
)
def process_email(
    self: DatabaseTask,
    email_id: int,
) -> dict:
    """
    Run an already-classified email through the action workflow.
    """

    db = SessionLocal()

    try:
        email = get_email_by_id(db=db, email_id=email_id)

        if email is None:
            logger.error(
                "process_email: email not found",
                extra={"email_id": email_id},
            )
            return {"email_id": email_id, "error": "not_found"}

        if email.status in _TERMINAL_STATUSES:
            logger.info(
                "process_email: skipping email (terminal status)",
                extra={
                    "email_id": email_id,
                    "workflow_status": email.status,
                },
            )
            return {
                "email_id": email_id,
                "workflow_status": email.status,
                "skipped": True,
            }

        workflow_service = WorkflowService()

        result = workflow_service.process_email(
            db=db,
            email_id=email_id,
        )

        logger.info(
            "process_email: completed",
            extra={
                "email_id": email_id,
                "workflow_status": result.workflow_status,
                "approval_id": result.approval_id,
                "error": result.error,
            },
        )

        return {
            "email_id": email_id,
            "workflow_status": result.workflow_status,
            "approval_id": result.approval_id,
            "execution_result": result.execution_result,
            "error": result.error,
        }

    except Exception as exc:
        logger.error(
            "process_email: failed with exception",
            exc_info=True,
            extra={
                "email_id": email_id,
                "error": str(exc),
            },
        )

        raise self.retry(
            exc=exc,
            countdown=10,
            max_retries=3,
        )

    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.workers.tasks.process_email_pipeline",
)
def process_email_pipeline(
    self: DatabaseTask,
    email_id: int,
) -> dict:
    """
    Run the complete InboxPilot pipeline:

        PENDING
          ↓
        Classification
          ↓
        Confidence Gate
          ↓
        REVIEW or CLASSIFIED
          ↓
        LangGraph workflow
    """

    db = SessionLocal()

    try:
        email = get_email_by_id(db=db, email_id=email_id)

        if email is None:
            logger.error(
                "process_email_pipeline: email not found",
                extra={"email_id": email_id},
            )
            return {"email_id": email_id, "error": "not_found"}

        if email.status in _TERMINAL_STATUSES:
            logger.info(
                "process_email_pipeline: skipping email (terminal status)",
                extra={
                    "email_id": email_id,
                    "workflow_status": email.status,
                },
            )
            return {
                "email_id": email_id,
                "workflow_status": email.status,
                "skipped": True,
            }

        logger.info(
            "process_email_pipeline: started",
            extra={"email_id": email_id},
        )

        pipeline = EmailPipeline()

        result = pipeline.process_email(
            db=db,
            email_id=email_id,
        )

        logger.info(
            "process_email_pipeline: completed",
            extra={
                "email_id": email_id,
                "workflow_status": result.workflow_status,
                "error": result.error,
            },
        )

        return {
            "email_id": result.email_id,
            "workflow_status": result.workflow_status,
            "category": (
                result.classification.category.value
                if result.classification is not None
                else None
            ),
            "confidence": (
                result.classification.confidence
                if result.classification is not None
                else None
            ),
            "action": (
                result.action_plan.action.value
                if result.action_plan is not None
                else None
            ),
            "risk_level": (
                result.action_plan.risk_level.value
                if result.action_plan is not None
                else None
            ),
            "requires_approval": (
                result.action_plan.requires_approval
                if result.action_plan is not None
                else False
            ),
            "approval_id": result.approval_id,
            "execution_result": result.execution_result,
            "error": result.error,
        }

    except Exception as exc:
        logger.error(
            "process_email_pipeline: failed with exception",
            exc_info=True,
            extra={
                "email_id": email_id,
                "error": str(exc),
            },
        )

        # Mark email as FAILED so it doesn't stay stuck in PENDING
        try:
            email_obj = get_email_by_id(db=db, email_id=email_id)
            if email_obj and email_obj.status in ("PENDING", "PROCESSING"):
                from app.repositories.email_repository import update_email_status
                update_email_status(db=db, email=email_obj, status="FAILED")
                logger.info(
                    "process_email_pipeline: marked email %d as FAILED",
                    email_id,
                )
        except Exception:
            pass

        raise self.retry(
            exc=exc,
            countdown=10,
            max_retries=3,
        )

    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.workers.tasks.ingest_all_gmail",
)
def ingest_all_gmail(self: DatabaseTask) -> dict:
    """
    Periodic task to ingest emails for all connected Google accounts.
    Uses per-account error isolation so one broken account cannot
    block ingestion for all others.
    """
    from app.services.email_ingestion import ingest_inbox_emails

    logger.info("[GMAIL_SYNC] cycle_started")

    db = SessionLocal()
    total_fetched = 0
    total_inserted = 0
    total_skipped = 0
    total_failed = 0
    total_queued = 0
    accounts_checked = 0
    accounts_succeeded = 0
    accounts_failed = 0

    try:
        accounts = db.query(GoogleAccount).filter(
            GoogleAccount.user_id.isnot(None)
        ).all()

        logger.info(
            "[GMAIL_SYNC] checking_connected_accounts count=%d",
            len(accounts),
        )

        for account in accounts:
            accounts_checked += 1

            logger.info(
                "[GMAIL_SYNC] account_checked integration_id=%d",
                account.id,
            )

            try:
                result = ingest_inbox_emails(
                    db=db,
                    account=account,
                    max_results=25,
                )
                fetched = result.get("fetched", 0)
                inserted = result.get("inserted", 0)
                skipped = result.get("skipped", 0)
                failed = result.get("failed", 0)
                queued = result.get("processing_queued", 0)

                total_fetched += fetched
                total_inserted += inserted
                total_skipped += skipped
                total_failed += failed
                total_queued += queued
                accounts_succeeded += 1

                logger.info(
                    "[GMAIL_SYNC] account_synced integration_id=%d "
                    "fetched=%d inserted=%d skipped=%d failed=%d queued=%d",
                    account.id,
                    fetched,
                    inserted,
                    skipped,
                    failed,
                    queued,
                )

            except Exception as account_exc:
                accounts_failed += 1
                logger.error(
                    "[GMAIL_SYNC] account_failed integration_id=%d error=%s",
                    account.id,
                    type(account_exc).__name__,
                    exc_info=True,
                )

        logger.info(
            "[GMAIL_SYNC] cycle_completed "
            "accounts_checked=%d accounts_succeeded=%d accounts_failed=%d "
            "messages_fetched=%d messages_inserted=%d "
            "duplicates_skipped=%d messages_failed=%d "
            "processing_tasks_queued=%d",
            accounts_checked,
            accounts_succeeded,
            accounts_failed,
            total_fetched,
            total_inserted,
            total_skipped,
            total_failed,
            total_queued,
        )

        return {
            "accounts_checked": accounts_checked,
            "accounts_succeeded": accounts_succeeded,
            "accounts_failed": accounts_failed,
            "fetched": total_fetched,
            "inserted": total_inserted,
            "skipped": total_skipped,
            "failed": total_failed,
            "processing_queued": total_queued,
        }

    except Exception as exc:
        logger.error(
            "[GMAIL_SYNC] cycle_failed error=%s",
            type(exc).__name__,
            exc_info=True,
        )
        raise self.retry(exc=exc, countdown=60, max_retries=3)
    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.workers.tasks.ingest_single_gmail",
)
def ingest_single_gmail(self: DatabaseTask, user_id: str) -> dict:
    """
    On-demand sync for a single user's Gmail account.
    Triggered by the manual sync endpoint.
    """
    from app.services.email_ingestion import ingest_inbox_emails

    logger.info("[GMAIL_SYNC] manual_sync_started user_id=%s", user_id)

    db = SessionLocal()

    try:
        account = (
            db.query(GoogleAccount)
            .filter(GoogleAccount.user_id == user_id)
            .first()
        )

        if account is None:
            logger.warning(
                "[GMAIL_SYNC] manual_sync: no Google account for user %s",
                user_id,
            )
            return {"error": "No Google account found"}

        result = ingest_inbox_emails(
            db=db,
            account=account,
            max_results=25,
        )

        logger.info(
            "[GMAIL_SYNC] manual_sync_completed user_id=%s "
            "fetched=%d inserted=%d",
            user_id,
            result.get("fetched", 0),
            result.get("inserted", 0),
        )

        return result

    except Exception as exc:
        logger.error(
            "[GMAIL_SYNC] manual_sync_failed user_id=%s error=%s",
            user_id,
            type(exc).__name__,
            exc_info=True,
        )
        raise self.retry(exc=exc, countdown=30, max_retries=3)

    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.workers.tasks.import_initial_gmail",
)
def import_initial_gmail(self: DatabaseTask, user_id: str) -> dict:
    """
    One-time task triggered when a user first connects their Gmail account.

    Fetches the 10 most recent emails and stores them with status ``IMPORTED``
    so the user's inbox is pre-populated.  These emails are NOT sent through
    the AI pipeline — only genuinely new emails arriving after the initial
    connection will be classified, planned, and executed.
    """
    from app.services.email_ingestion import ingest_inbox_emails

    db = SessionLocal()

    try:
        account = (
            db.query(GoogleAccount)
            .filter(GoogleAccount.user_id == user_id)
            .first()
        )

        if account is None:
            logger.warning(
                "import_initial_gmail: no Google account found for user %s",
                user_id,
            )
            return {"error": "No Google account found"}

        result = ingest_inbox_emails(
            db=db,
            account=account,
            max_results=10,
            import_only=True,
        )

        logger.info(
            "import_initial_gmail completed for user %s: fetched %d, imported %d",
            user_id,
            result.get("fetched", 0),
            result.get("inserted", 0),
        )

        return result

    except Exception as exc:
        logger.error(
            "import_initial_gmail: failed for user %s",
            user_id,
            exc_info=True,
        )
        raise self.retry(exc=exc, countdown=30, max_retries=3)

    finally:
        db.close()


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.workers.tasks.execute_approved_action",
)
def execute_approved_action(self: DatabaseTask, approval_id: int) -> dict:
    from app.services.approval_execution_service import ApprovalExecutionService
    db = SessionLocal()
    try:
        logger.info(
            "execute_approved_action: started for approval %d",
            approval_id,
        )
        result = ApprovalExecutionService.execute_approved(
            db=db,
            approval_id=approval_id,
        )
        
        # We optionally sync telegram status here.
        from app.api.routes.approvals import _sync_telegram_status
        _sync_telegram_status(db, approval_id, "✅ Executed successfully")

        logger.info(
            "execute_approved_action: completed for approval %d",
            approval_id,
        )
        return {
            "approval_id": approval_id,
            "status": "EXECUTED",
            "execution_result": result,
        }
    except Exception as exc:
        logger.error(
            "execute_approved_action: failed with exception",
            exc_info=True,
            extra={
                "approval_id": approval_id,
                "error": str(exc),
            },
        )
        
        from app.api.routes.approvals import _sync_telegram_status
        _sync_telegram_status(db, approval_id, f"❌ Execution failed: {str(exc)}")
        
        raise self.retry(exc=exc, countdown=10, max_retries=3)
    finally:
        db.close()

@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.workers.tasks.cleanup_old_emails_task",
)
def cleanup_old_emails_task(self: DatabaseTask) -> dict:
    """
    Periodic task to delete emails older than 7 days to save database storage.
    """
    from app.repositories.email_repository import delete_old_emails
    db = SessionLocal()
    
    try:
        deleted_count = delete_old_emails(db=db, days_old=7)
        logger.info("cleanup_old_emails_task: successfully deleted %d old emails.", deleted_count)
        return {"deleted_emails": deleted_count}
    except Exception as exc:
        logger.error("cleanup_old_emails_task: failed with exception", exc_info=True)
        raise self.retry(exc=exc, countdown=60, max_retries=3)
    finally:
        db.close()