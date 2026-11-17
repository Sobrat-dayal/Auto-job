"""Centralized service container managing dependency wiring, lifecycles, and health state."""

import logging
from datetime import UTC, datetime
from typing import Any

from app.core.config import settings
from app.db.engine import engine
from app.db.migrations import init_database_schema
from app.events.bus import EventBus
from app.events.models import EventType
from app.execution.handlers import HandlerRegistry
from app.execution.manager import TaskExecutionManager
from app.schemas.events import EventEnvelope
from app.security.vault import vault
from app.workers.manager import WorkerManager

logger = logging.getLogger("autonom.services")


class ServiceContainer:
    """Dependency injection container holding foundational backend singletons and database persistence."""

    def __init__(self) -> None:
        self.event_bus = EventBus()
        self.worker_manager = WorkerManager()
        self.handler_registry = HandlerRegistry()
        self.task_manager = TaskExecutionManager(
            event_bus=self.event_bus,
            worker_manager=self.worker_manager,
            handler_registry=self.handler_registry,
        )
        self.start_time: datetime = datetime.now(UTC)
        self.is_ready = False

    @property
    def uptime_seconds(self) -> float:
        """Returns elapsed uptime in seconds."""
        return round((datetime.now(UTC) - self.start_time).total_seconds(), 2)

    def reset(self) -> None:
        """Resets container components to a fresh initial state."""
        self.event_bus = EventBus()
        self.worker_manager = WorkerManager()
        self.handler_registry = HandlerRegistry()
        self.task_manager = TaskExecutionManager(
            event_bus=self.event_bus,
            worker_manager=self.worker_manager,
            handler_registry=self.handler_registry,
        )
        self.start_time = datetime.now(UTC)
        self.is_ready = False

    async def initialize(self) -> None:
        """Sequential startup initialization of backend subsystems, vault, and database."""
        if not self.event_bus._is_running or not self.worker_manager._is_running:
            self.reset()

        logger.info("Initializing ServiceContainer subsystems...")
        settings.ensure_directories()

        # 1. Initialize Cryptographic Vault
        try:
            vault.initialize()
            logger.info("Cryptographic vault initialized.")
        except Exception as exc:
            logger.error(f"Failed to initialize vault: {exc}")

        # 2. Initialize Database Schema
        try:
            await init_database_schema(engine)
            logger.info("Database schema verified.")
        except Exception as exc:
            logger.error(f"Failed to initialize database schema: {exc}")
            raise

        # 3. Startup Task Reconciliation
        try:
            await self.task_manager.reconcile_on_startup()
        except Exception as exc:
            logger.warning(f"Error during startup task reconciliation: {exc}")

        # 3b. Startup Workflow Orchestration Reconciliation
        try:
            from app.orchestration.supervisor import get_supervisor_agent
            await get_supervisor_agent().reconcile_active_workflows()
        except Exception as exc:
            logger.warning(f"Error during startup workflow reconciliation: {exc}")

        # 3c. Startup Emergency Stop State Loading
        try:
            from app.security.authorization.emergency import get_emergency_stop_controller
            await get_emergency_stop_controller().initialize()
        except Exception as exc:
            logger.warning(f"Error during startup emergency stop initialization: {exc}")

        # 3d. Startup Memory Service Index Warm-up
        try:
            from app.memory.service import get_memory_service
            await get_memory_service().initialize()
        except Exception as exc:
            logger.warning(f"Error during startup memory service initialization: {exc}")

        # 4. Start worker manager loop
        await self.worker_manager.start(self.task_manager)

        # 5. Mark system ready
        self.is_ready = True

        # 6. Emit system.started event
        await self.event_bus.publish(
            EventEnvelope(
                event_type=EventType.SYSTEM_STARTED,
                source="autonom.system",
                payload={
                    "uptime_seconds": self.uptime_seconds,
                    "workers": self.worker_manager.concurrency,
                    "queue_capacity": self.worker_manager.max_queue_size,
                    "handlers": self.handler_registry.list_types(),
                },
            )
        )
        logger.info("ServiceContainer initialized successfully; readiness set to True.")

    async def shutdown(self) -> None:
        """Orderly shutdown of background workers, event bus, database, and active work."""
        logger.info("ServiceContainer beginning shutdown sequence...")
        # 1. Cease readiness immediately
        self.is_ready = False

        # 2. Emit system.stopping event
        try:
            await self.event_bus.publish(
                EventEnvelope(
                    event_type=EventType.SYSTEM_STOPPING,
                    source="autonom.system",
                    payload={"uptime_seconds": self.uptime_seconds},
                )
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Error publishing system.stopping event: {exc}")

        # 3. Stop background workers
        await self.worker_manager.stop(timeout=5.0)

        # 4. Close event bus
        await self.event_bus.close()

        # 5. Dispose database engine connections
        try:
            await engine.dispose()
        except Exception as exc:  # noqa: BLE001
            logger.warning(f"Error disposing database engine: {exc}")

        logger.info("ServiceContainer shutdown complete.")

    def get_readiness_checks(self) -> dict[str, bool]:
        """Returns component readiness health check results."""
        return {
            "service_container": self.is_ready,
            "worker_manager": self.worker_manager.is_running,
            "event_bus": self.event_bus._is_running,
            "task_manager": True,
            "database": True,
        }

    def get_system_status(self) -> dict[str, Any]:
        """Produces a snapshot dictionary of system operations."""
        worker_status = self.worker_manager.get_status()
        return {
            "status": "operational" if self.is_ready else "degraded",
            "uptime_seconds": self.uptime_seconds,
            "active_tasks": self.task_manager.active_tasks_count,
            "queued_tasks": self.worker_manager.queue_size,
            "workers": {
                "total": worker_status.total_workers,
                "active": worker_status.active_workers,
                "idle": worker_status.idle_workers,
                "max_capacity": worker_status.max_capacity,
            },
            "event_subscribers": self.event_bus.subscriber_count,
            "timestamp": datetime.now(UTC),
        }


# Global singleton container instance
_container: ServiceContainer | None = None


def get_container() -> ServiceContainer:
    """Returns the shared ServiceContainer singleton, initializing if needed."""
    global _container
    if _container is None:
        _container = ServiceContainer()
    return _container


def reset_container() -> ServiceContainer:
    """Forces creation of a new ServiceContainer instance (useful for test isolation)."""
    global _container
    _container = ServiceContainer()
    return _container
