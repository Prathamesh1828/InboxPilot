import logging

from celery import Celery
from celery.schedules import crontab
from celery.signals import worker_ready, beat_init

from app.core.settings import settings
from app.core.redis import get_celery_ssl_config, _clean_redis_url

logger = logging.getLogger(__name__)

_broker_url = _clean_redis_url(settings.redis_url)

celery_app = Celery(
    "inboxpilot",
    broker=_broker_url,
    backend=_broker_url,
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
        "ingest-all-gmail-frequent": {
            "task": "app.workers.tasks.ingest_all_gmail",
            "schedule": 30.0,  # 30 seconds for near real-time ingestion
            "options": {"expires": 25},  # expire before next cycle
        },
        "cleanup-old-emails-daily": {
            "task": "app.workers.tasks.cleanup_old_emails_task",
            "schedule": crontab(hour=0, minute=0),  # Run daily at midnight
        },
    },
)

# Apply TLS configuration when using rediss:// URLs (e.g. Render Key-Value).
ssl_config = get_celery_ssl_config()
if ssl_config:
    celery_app.conf.update(**ssl_config)
    logger.info("[CELERY] TLS configuration applied for broker and backend")


# ---------------------------------------------------------------------------
# Lifecycle signals — observability for Render logs
# ---------------------------------------------------------------------------

@worker_ready.connect
def _on_worker_ready(**kwargs):
    logger.info("[CELERY] Worker ready — listening for tasks")


@beat_init.connect
def _on_beat_init(**kwargs):
    logger.info("[CELERY] Beat scheduler started — ingestion cycle scheduled")