from celery import Celery

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
)