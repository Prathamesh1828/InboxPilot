from celery import Task

from app.db.database import SessionLocal
from app.services.workflow_service import WorkflowService
from app.workers.celery_app import celery_app


class DatabaseTask(Task):
    """Base Celery task that provides database-session handling."""


@celery_app.task(
    bind=True,
    base=DatabaseTask,
    name="app.workers.tasks.process_email",
)
def process_email(self: DatabaseTask, email_id: int) -> dict:
    db = SessionLocal()

    try:
        workflow_service = WorkflowService()

        result = workflow_service.process_email(
            db=db,
            email_id=email_id,
        )

        return {
            "email_id": email_id,
            "workflow_status": result.workflow_status,
            "approval_id": result.approval_id,
            "execution_result": result.execution_result,
            "error": result.error,
        }

    except Exception as exc:
        raise self.retry(
            exc=exc,
            countdown=10,
            max_retries=3,
        )

    finally:
        db.close()