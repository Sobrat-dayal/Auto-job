"""Dedicated MTA worker thread supervisor for UI Automation (Stage 17)."""

import asyncio
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeoutError
from datetime import UTC, datetime
import logging
from typing import Any, Callable, TypeVar

from app.computer.uia.com_runtime import COMWorkerContext

logger = logging.getLogger("autonom.computer.uia.workers")

T = TypeVar("T")


class UIAWorkerSupervisor:
    """Supervises dedicated MTA worker threads for Microsoft UI Automation operations."""

    def __init__(self, max_workers: int = 4) -> None:
        self.max_workers = max_workers
        self._executor = ThreadPoolExecutor(
            max_workers=max_workers,
            thread_name_prefix="UIAWorkerThread",
        )
        self._active_jobs = 0
        self._total_jobs_executed = 0
        self._failed_jobs_count = 0
        self._last_heartbeat = datetime.now(UTC)

    def _execute_sync(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        """Worker wrapper running with MTA COM initialization and desktop attachment."""
        with COMWorkerContext():
            return func(*args, **kwargs)

    async def execute_uia_call(
        self,
        func: Callable[..., T],
        *args: Any,
        timeout_seconds: float = 15.0,
        **kwargs: Any,
    ) -> T:
        """Executes a blocking UI Automation function on a dedicated MTA thread with timeout enforcement."""
        loop = asyncio.get_running_loop()
        self._active_jobs += 1
        self._last_heartbeat = datetime.now(UTC)

        try:
            future = loop.run_in_executor(
                self._executor,
                self._execute_sync,
                func,
                *args,
                **kwargs,
            )
            result = await asyncio.wait_for(future, timeout=timeout_seconds)
            self._total_jobs_executed += 1
            return result
        except asyncio.TimeoutError:
            self._failed_jobs_count += 1
            logger.error(f"UIA worker operation timed out after {timeout_seconds}s")
            raise TimeoutError(f"UI Automation operation exceeded timeout limit of {timeout_seconds}s")
        except Exception as e:
            self._failed_jobs_count += 1
            logger.error(f"UIA worker call error: {e}")
            raise
        finally:
            self._active_jobs = max(0, self._active_jobs - 1)
            self._last_heartbeat = datetime.now(UTC)

    def get_health_status(self) -> dict[str, Any]:
        """Returns worker pool telemetry and health indicators."""
        return {
            "max_workers": self.max_workers,
            "active_workers": self._active_jobs,
            "total_jobs_executed": self._total_jobs_executed,
            "failed_jobs_count": self._failed_jobs_count,
            "last_heartbeat": self._last_heartbeat.isoformat(),
            "status": "healthy" if self._failed_jobs_count < 10 else "degraded",
        }

    def shutdown(self) -> None:
        """Gracefully terminates worker thread pool."""
        logger.info("Shutting down UIA worker supervisor...")
        self._executor.shutdown(wait=False, cancel_futures=True)


uia_worker_supervisor = UIAWorkerSupervisor(max_workers=4)
