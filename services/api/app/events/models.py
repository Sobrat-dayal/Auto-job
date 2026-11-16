"""Event type definitions and constants for the AUTONOM event bus."""


class EventType:
    # System events
    SYSTEM_STARTED = "system.started"
    SYSTEM_STOPPING = "system.stopping"
    SERVICE_HEALTH_CHANGED = "service.health_changed"

    # Worker events
    WORKER_STARTED = "worker.started"
    WORKER_STOPPED = "worker.stopped"

    # Task lifecycle events
    TASK_CREATED = "task.created"
    TASK_QUEUED = "task.queued"
    TASK_STARTED = "task.started"
    TASK_PROGRESS = "task.progress"
    TASK_COMPLETED = "task.completed"
    TASK_FAILED = "task.failed"
    TASK_CANCELLED = "task.cancelled"
