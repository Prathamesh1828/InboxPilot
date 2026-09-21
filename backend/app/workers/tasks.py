import logging

from celery import Task

from app.db.database import SessionLocal
from app.repositories.email_repository import get_email_by_id
from app.services.email_pipeline import EmailPipeline
from app.services.workflow_service import WorkflowService
from app.workers.celery_app import celery_app

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