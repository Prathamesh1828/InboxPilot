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
    """
    from app.services.email_ingestion import ingest_inbox_emails

    db = SessionLocal()
    total_fetched = 0
    total_inserted = 0
    total_failed = 0
    accounts_processed = 0

    try:
        accounts = db.query(GoogleAccount).all()
        for account in accounts:
            try:
                result = ingest_inbox_emails(db=db, account=account, max_results=10)
                total_fetched += result.get("fetched", 0)
                total_inserted += result.get("inserted", 0)
                total_failed += result.get("failed", 0)
                accounts_processed += 1
            except Exception as account_exc:
                logger.error(
                    "Failed to ingest for account %s: %s",
                    account.email,
                    account_exc,
                    exc_info=True,
                )
                
        logger.info(
            "ingest_all_gmail completed: processed %d accounts, fetched %d, inserted %d, failed %d",
            accounts_processed, total_fetched, total_inserted, total_failed
        )
        return {
            "accounts_processed": accounts_processed,
            "fetched": total_fetched,
            "inserted": total_inserted,
            "failed": total_failed,
        }

    except Exception as exc:
        logger.error("ingest_all_gmail: failed with exception", exc_info=True)
        raise self.retry(exc=exc, countdown=60, max_retries=3)
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