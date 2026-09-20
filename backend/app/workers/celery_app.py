from celery import Celery


celery_app = Celery(
    "inboxpilot",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
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