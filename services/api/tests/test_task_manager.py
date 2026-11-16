"""Unit tests for TaskExecutionManager lifecycle, execution, cancellation, and timeouts."""

import asyncio

import pytest

from app.core.exceptions import TaskNotFoundError, UnknownTaskTypeError
from app.events.bus import EventBus
from app.execution.handlers import HandlerRegistry
from app.execution.manager import TaskExecutionManager
from app.schemas.tasks import TaskCreateRequest, TaskState
from app.workers.manager import WorkerManager


@pytest.mark.asyncio
async def test_unknown_task_type_rejected():
    bus = EventBus()
    workers = WorkerManager(concurrency=2, max_queue_size=10)
    registry = HandlerRegistry()
    manager = TaskExecutionManager(bus, workers, registry)
    await workers.start(manager)

    with pytest.raises(UnknownTaskTypeError) as exc:
        await manager.create_task(TaskCreateRequest(task_type="malicious.exec", payload={}))

    assert exc.value.code == "UNKNOWN_TASK_TYPE"
    await workers.stop()
    await bus.close()


@pytest.mark.asyncio
async def test_compute_echo_task_completes():
    bus = EventBus()
    workers = WorkerManager(concurrency=2, max_queue_size=10)
    registry = HandlerRegistry()
    manager = TaskExecutionManager(bus, workers, registry)
    await workers.start(manager)

    task = await manager.create_task(
        TaskCreateRequest(
            task_type="compute.echo",
            payload={"text": "AUTONOM", "repeat": 2},
        )
    )
    assert task.state in (TaskState.CREATED, TaskState.QUEUED, TaskState.RUNNING)

    # Wait for completion
    for _ in range(50):
        await asyncio.sleep(0.05)
        latest = manager.get_task(task.task_id)
        if latest.state.is_terminal:
            break

    final = manager.get_task(task.task_id)
    assert final.state == TaskState.COMPLETED
    assert final.progress == 100.0
    assert final.result["transformed_text"] == "MONOTUA MONOTUA"

    result_resp = manager.get_task_result(task.task_id)
    assert result_resp.state == TaskState.COMPLETED
    assert result_resp.result is not None

    await workers.stop()
    await bus.close()


@pytest.mark.asyncio
async def test_task_cooperative_cancellation():
    bus = EventBus()
    workers = WorkerManager(concurrency=2, max_queue_size=10)
    registry = HandlerRegistry()
    manager = TaskExecutionManager(bus, workers, registry)
    await workers.start(manager)

    # Submit multi-step task with delay
    task = await manager.create_task(
        TaskCreateRequest(
            task_type="test.sleep_progress",
            payload={"steps": 10, "step_delay": 0.1},
        )
    )

    # Let it start
    await asyncio.sleep(0.15)

    # Request cancellation
    cancel_resp = await manager.cancel_task(task.task_id, reason="User test cancellation")
    assert cancel_resp.cancelled is True

    # Wait for completion
    for _ in range(30):
        await asyncio.sleep(0.05)
        latest = manager.get_task(task.task_id)
        if latest.state.is_terminal:
            break

    final = manager.get_task(task.task_id)
    assert final.state == TaskState.CANCELLED

    await workers.stop()
    await bus.close()


@pytest.mark.asyncio
async def test_task_simulated_failure():
    bus = EventBus()
    workers = WorkerManager(concurrency=2, max_queue_size=10)
    registry = HandlerRegistry()
    manager = TaskExecutionManager(bus, workers, registry)
    await workers.start(manager)

    task = await manager.create_task(
        TaskCreateRequest(
            task_type="test.sleep_progress",
            payload={"steps": 5, "step_delay": 0.05, "fail_at_step": 2},
        )
    )

    for _ in range(30):
        await asyncio.sleep(0.05)
        latest = manager.get_task(task.task_id)
        if latest.state.is_terminal:
            break

    final = manager.get_task(task.task_id)
    assert final.state == TaskState.FAILED
    assert final.error is not None
    assert "Simulated execution failure" in final.error.message

    await workers.stop()
    await bus.close()


@pytest.mark.asyncio
async def test_task_timeout_handling():
    bus = EventBus()
    workers = WorkerManager(concurrency=2, max_queue_size=10)
    registry = HandlerRegistry()
    manager = TaskExecutionManager(bus, workers, registry)
    await workers.start(manager)

    # Submit task with 0.1s timeout, but steps will take 0.5s total
    task = await manager.create_task(
        TaskCreateRequest(
            task_type="test.sleep_progress",
            payload={"steps": 5, "step_delay": 0.1},
            timeout_seconds=0.15,
        )
    )

    for _ in range(30):
        await asyncio.sleep(0.05)
        latest = manager.get_task(task.task_id)
        if latest.state.is_terminal:
            break

    final = manager.get_task(task.task_id)
    assert final.state == TaskState.FAILED
    assert final.error is not None
    assert final.error.code == "TASK_TIMEOUT"

    await workers.stop()
    await bus.close()


@pytest.mark.asyncio
async def test_missing_task_raises_not_found():
    bus = EventBus()
    workers = WorkerManager(concurrency=1, max_queue_size=10)
    registry = HandlerRegistry()
    manager = TaskExecutionManager(bus, workers, registry)

    with pytest.raises(TaskNotFoundError):
        manager.get_task("nonexistent-task-id")

    with pytest.raises(TaskNotFoundError):
        await manager.cancel_task("nonexistent-task-id")
