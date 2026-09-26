from celery import Celery
from celery.schedules import crontab

from app.core.settings import settings

celery_app = Celery(
    "inboxpilot",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.tasks"],
)

celery_app.conf.update(
    # Re-queue tasks if the worker crashes mid-execution.
    task_acks_late=True,
    task_reject_on_worker_lost=True,

    # Bounded execution time (seconds).
    task_time_limit=300,
    task_soft_time_limit=240,

    # Restart workers periodically to reclaim memory.
    worker_max_tasks_per_child=100,

    # Serialization.
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],

    # Beat schedule
    beat_schedule={
        "ingest-all-gmail-every-2-minutes": {
            "task": "app.workers.tasks.ingest_all_gmail",
            "schedule": 120.0,  # 2 minutes — safe with incremental History API
            "options": {"expires": 110},  # expire before next cycle
        },
        "cleanup-old-emails-daily": {
            "task": "app.workers.tasks.cleanup_old_emails_task",
            "schedule": crontab(hour=0, minute=0),  # Run daily at midnight
        },
    },
)