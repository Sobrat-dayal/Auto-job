"""Repository for persistent task state, worker runs, and startup reconciliation."""

from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TaskModel, WorkerRunModel, utc_now
from app.repositories.base import BaseRepository
from app.schemas.tasks import TaskState


class TaskRepository(BaseRepository[TaskModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_task(
        self,
        task_id: str,
        task_type: str,
        priority: str = "normal",
        title: str | None = None,
        payload: dict[str, Any] | None = None,
        correlation_id: str | None = None,
        timeout_seconds: float = 60.0,
    ) -> TaskModel:
        task = TaskModel(
            id=task_id,
            task_type=task_type,
            title=title or f"Task {task_type}",
            status=TaskState.QUEUED.value,
            priority=priority,
            progress=0.0,
            progress_message="Task enqueued for worker execution",
            input_payload_json=payload or {},
            correlation_id=correlation_id,
            timeout_seconds=timeout_seconds,
            version=1,
        )
        self.session.add(task)
        await self.session.flush()
        return task

    async def get_task(self, task_id: str) -> TaskModel | None:
        result = await self.session.execute(select(TaskModel).where(TaskModel.id == task_id))
        return result.scalar_one_or_none()

    async def update_task_state(
        self,
        task_id: str,
        new_state: str,
        progress: float | None = None,
        progress_message: str | None = None,
    ) -> TaskModel | None:
        task = await self.get_task(task_id)
        if not task:
            return None

        task.status = new_state
        task.version += 1
        if progress is not None:
            task.progress = progress
        if progress_message is not None:
            task.progress_message = progress_message

        if new_state == TaskState.RUNNING.value and task.started_at is None:
            task.started_at = utc_now()
        elif new_state in (TaskState.COMPLETED.value, TaskState.FAILED.value, TaskState.CANCELLED.value):
            task.completed_at = utc_now()

        await self.session.flush()
        return task

    async def complete_task(self, task_id: str, result_json: dict[str, Any]) -> TaskModel | None:
        task = await self.get_task(task_id)
        if not task:
            return None

        task.status = TaskState.COMPLETED.value
        task.progress = 100.0
        task.progress_message = "Task completed successfully"
        task.output_result_json = result_json
        task.completed_at = utc_now()
        task.version += 1

        await self.session.flush()
        return task

    async def fail_task(self, task_id: str, error_info_json: dict[str, Any]) -> TaskModel | None:
        task = await self.get_task(task_id)
        if not task:
            return None

        task.status = TaskState.FAILED.value
        task.error_info_json = error_info_json
        task.progress_message = error_info_json.get("message", "Task execution failed")
        task.completed_at = utc_now()
        task.version += 1

        await self.session.flush()
        return task

    async def cancel_task(self, task_id: str, reason: str = "User requested cancellation") -> TaskModel | None:
        task = await self.get_task(task_id)
        if not task:
            return None

        task.status = TaskState.CANCELLED.value
        task.progress_message = reason
        task.completed_at = utc_now()
        task.version += 1

        await self.session.flush()
        return task

    async def list_tasks(
        self,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[TaskModel]:
        query = select(TaskModel).order_by(TaskModel.created_at.desc())
        if status:
            query = query.where(TaskModel.status == status)
        query = query.limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def record_worker_run(
        self,
        task_id: str,
        worker_id: str,
        start_time: datetime,
        end_time: datetime,
        execution_result_json: dict[str, Any] | None = None,
        failure_class: str | None = None,
    ) -> WorkerRunModel:
        duration = (end_time - start_time).total_seconds()
        run = WorkerRunModel(
            task_id=task_id,
            worker_id=worker_id,
            start_time=start_time,
            end_time=end_time,
            execution_result_json=execution_result_json,
            failure_class=failure_class,
            duration_seconds=duration,
        )
        self.session.add(run)
        await self.session.flush()
        return run

    async def reconcile_interrupted_tasks(self) -> list[TaskModel]:
        """Identifies tasks that were active (Running/Planning) when backend previously stopped."""
        query = select(TaskModel).where(
            TaskModel.status.in_([TaskState.RUNNING.value, TaskState.PLANNING.value])
        )
        result = await self.session.execute(query)
        interrupted = list(result.scalars().all())

        now = utc_now()
        for task in interrupted:
            task.status = TaskState.FAILED.value
            task.completed_at = now
            task.progress_message = "INTERRUPTED: Process stopped unexpectedly while task was active."
            task.error_info_json = {
                "code": "TASK_INTERRUPTED_CRASH",
                "message": "Backend process was terminated during task execution.",
                "retryable": False,
            }
            task.version += 1

        if interrupted:
            await self.session.flush()

        return interrupted
