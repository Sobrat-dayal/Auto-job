"""Asynchronous background worker manager handling task dispatch, concurrency, and shutdown."""

import asyncio
import logging
from typing import TYPE_CHECKING

from app.core.config import settings
from app.core.exceptions import QueueFullError
from app.schemas.system import WorkerInfo, WorkerListResponse
from app.schemas.tasks import TaskPriority

if TYPE_CHECKING:
    from app.execution.manager import TaskExecutionManager

logger = logging.getLogger("autonom.workers")


class WorkerManager:
    """Manages an asynchronous pool of background workers executing queued tasks."""

    def __init__(
        self,
        concurrency: int | None = None,
        max_queue_size: int | None = None,
    ) -> None:
        self.concurrency = concurrency or settings.max_concurrent_workers
        self.max_queue_size = max_queue_size or settings.max_queued_tasks
        self._queue: asyncio.Queue[str] = asyncio.Queue(maxsize=self.max_queue_size)
        self._workers: list[asyncio.Task] = []
        self._worker_infos: dict[str, WorkerInfo] = {}
        self._manager: TaskExecutionManager | None = None
        self._is_running = False

    @property
    def queue_size(self) -> int:
        """Returns the current number of tasks waiting in the queue."""
        return self._queue.qsize()

    @property
    def is_running(self) -> bool:
        return self._is_running

    async def start(self, manager: "TaskExecutionManager") -> None:
        """Initializes the worker pool and begins consuming from the task queue."""
        self._manager = manager
        self._is_running = True

        for i in range(self.concurrency):
            worker_id = f"worker-{i + 1:02d}"
            info = WorkerInfo(worker_id=worker_id, status="idle")
            self._worker_infos[worker_id] = info
            task = asyncio.create_task(self._worker_loop(worker_id), name=worker_id)
            self._workers.append(task)

        logger.info(
            f"WorkerManager started with {self.concurrency} concurrent workers (Queue capacity: {self.max_queue_size})"
        )

    async def enqueue_task(self, task_id: str, priority: TaskPriority = TaskPriority.NORMAL) -> None:
        """Enqueues a task for worker execution, rejecting with QueueFullError if capacity is exceeded."""
        if not self._is_running:
            raise RuntimeError("WorkerManager is not running.")

        try:
            self._queue.put_nowait(task_id)
        except asyncio.QueueFull:
            raise QueueFullError(
                current_size=self._queue.qsize(),
                max_size=self.max_queue_size,
            )

    async def _worker_loop(self, worker_id: str) -> None:
        """Main loop for an individual asynchronous worker."""
        logger.debug(f"Worker {worker_id} started loop.")
        while self._is_running:
            try:
                task_id = await self._queue.get()
            except asyncio.CancelledError:
                break

            info = self._worker_infos[worker_id]
            info.status = "busy"
            info.active_task_id = task_id

            try:
                if self._manager:
                    await self._manager.execute_task(task_id, worker_id=worker_id)
                info.tasks_completed += 1
            except asyncio.CancelledError:
                logger.info(f"Worker {worker_id} cancelled during task {task_id}.")
                info.tasks_failed += 1
                break
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"Worker {worker_id} encountered error executing task {task_id}: {exc}")
                info.tasks_failed += 1
            finally:
                info.status = "idle"
                info.active_task_id = None
                self._queue.task_done()

        self._worker_infos[worker_id].status = "stopped"
        logger.debug(f"Worker {worker_id} exited loop.")

    def get_status(self) -> WorkerListResponse:
        """Returns the current operational snapshot of all workers."""
        workers = list(self._worker_infos.values())
        active = sum(1 for w in workers if w.status == "busy")
        idle = sum(1 for w in workers if w.status == "idle")
        return WorkerListResponse(
            workers=workers,
            total_workers=len(workers),
            active_workers=active,
            idle_workers=idle,
            max_capacity=self.concurrency,
        )

    async def stop(self, timeout: float = 5.0) -> None:
        """Gracefully shuts down the worker pool, cancelling active work with bounded timeout."""
        self._is_running = False
        for info in self._worker_infos.values():
            info.status = "shutting_down"

        for task in self._workers:
            task.cancel()

        if self._workers:
            await asyncio.gather(*self._workers, return_exceptions=True)

        self._workers.clear()
        logger.info("WorkerManager stopped.")
