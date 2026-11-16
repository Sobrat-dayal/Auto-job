# AUTONOM — Failure Handling, Circuit Breakers & Recovery (Stage 03)

This document specifies the exception taxonomy, circuit breaking patterns, backpressure policies, and automated recovery procedures in **AUTONOM**.

---

## 1. Domain Exception Hierarchy

AUTONOM implements an explicit domain exception hierarchy (`app/core/exceptions.py`):

```mermaid
graph TD
    AutonomException[AutonomException: code, message, status_code, details]

    AutonomException --> TaskException[Task Exceptions]
    TaskException --> TaskNotFoundError[TaskNotFoundError (404)]
    TaskException --> InvalidTaskTransitionError[InvalidTaskTransitionError (409)]
    TaskException --> UnknownTaskTypeError[UnknownTaskTypeError (400)]
    TaskException --> TaskExecutionError[TaskExecutionError (500)]
    TaskException --> TaskTimeoutError[TaskTimeoutError (504)]
    TaskException --> TaskCancelledError[TaskCancelledError (400)]

    AutonomException --> WorkerException[Worker & Resource Exceptions]
    WorkerException --> QueueFullError[QueueFullError (429)]
    WorkerException --> WorkerCapacityError[WorkerCapacityError (503)]
    WorkerException --> ServiceUnavailableError[ServiceUnavailableError (503)]

    AutonomException --> SecurityException[Security Exceptions]
    SecurityException --> AuthenticationError[AuthenticationError (401)]
    SecurityException --> AuthorizationError[AuthorizationError (403)]
```

Every domain exception translates to a standardized HTTP JSON payload:

```json
{
  "code": "INVALID_STATE_TRANSITION",
  "message": "Cannot transition task from 'completed' to 'running'",
  "status_code": 409,
  "details": { "current_state": "completed", "requested_state": "running" },
  "timestamp": "2026-11-16T14:00:00Z",
  "retryable": false
}
```

---

## 2. Backpressure & Queue Saturation Policy

Under high system load, AUTONOM defends system responsiveness through explicit backpressure:

1. **Queue Capacity Limit**: The worker queue has a maximum capacity of 50 tasks (`max_queued_tasks`).
2. **Rejection Policy**: If a client attempts to enqueue a task when the queue is saturated, the system immediately returns `429 Too Many Requests` (`QueueFullError`) with `retryable: true`.
3. **Slow Subscriber Drop**: If an SSE subscriber lags behind the event broadcast, events are skipped or the oldest event is evicted from the subscriber queue, preventing event queue bloat and memory leaks.

---

## 3. Worker Crash Recovery & Dead-Letter Handling

Workers run within an isolated execution loop:

1. **Uncaught Handler Exceptions**: If a `TaskHandler` throws an unexpected runtime exception, it is caught at the worker boundary, logged with a structured traceback, and converted into a `TaskExecutionError`. The task is transitioned to `failed`, and the worker immediately transitions back to `idle` to process the next queue item.
2. **Worker Pool Self-Healing**: If a worker coroutine unexpectedly terminates, the `WorkerManager` logs the event, marks the worker as stopped, and creates a replacement worker to maintain pool capacity.
3. **Cooperative Cancellation Rollback**: If a task is cancelled, any partial state is cleaned up by the handler before raising `TaskCancelledError`.
