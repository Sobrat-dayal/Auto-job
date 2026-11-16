"""Unit tests for WorkerManager concurrency, queue bounds, and task dispatch."""

import pytest

from app.core.exceptions import QueueFullError
from app.events.bus import EventBus
from app.execution.handlers import HandlerRegistry
from app.execution.manager import TaskExecutionManager
from app.schemas.tasks import TaskPriority
from app.workers.manager import WorkerManager


@pytest.mark.asyncio
async def test_worker_pool_concurrency_and_status():
    bus = EventBus()
    workers = WorkerManager(concurrency=3, max_queue_size=10)
    registry = HandlerRegistry()
    manager = TaskExecutionManager(bus, workers, registry)

    await workers.start(manager)
    status = workers.get_status()
    assert status.total_workers == 3
    assert status.max_capacity == 3
    assert status.idle_workers == 3
    assert status.active_workers == 0

    await workers.stop()
    await bus.close()


@pytest.mark.asyncio
async def test_queue_saturation_raises_error():
    bus = EventBus()
    # Tiny queue with 0 workers consuming
    workers = WorkerManager(concurrency=0, max_queue_size=2)
    workers._is_running = True

    await workers.enqueue_task("task-1", TaskPriority.NORMAL)
    await workers.enqueue_task("task-2", TaskPriority.NORMAL)

    with pytest.raises(QueueFullError) as exc:
        await workers.enqueue_task("task-3", TaskPriority.NORMAL)

    assert exc.value.code == "QUEUE_SATURATED"
    assert exc.value.status_code == 429
    await workers.stop()
    await bus.close()
