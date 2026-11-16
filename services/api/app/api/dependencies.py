"""FastAPI endpoint dependencies for service injection and security."""

from typing import Annotated

from fastapi import Depends

from app.core.security import AuthContext, require_auth
from app.events.bus import EventBus
from app.execution.handlers import HandlerRegistry
from app.execution.manager import TaskExecutionManager
from app.services.service_container import ServiceContainer, get_container
from app.workers.manager import WorkerManager


def get_service_container() -> ServiceContainer:
    """Dependency injecting the root service container."""
    return get_container()


ContainerDep = Annotated[ServiceContainer, Depends(get_service_container)]


def get_task_manager(container: ContainerDep) -> TaskExecutionManager:
    return container.task_manager


def get_worker_manager(container: ContainerDep) -> WorkerManager:
    return container.worker_manager


def get_event_bus(container: ContainerDep) -> EventBus:
    return container.event_bus


def get_handler_registry(container: ContainerDep) -> HandlerRegistry:
    return container.handler_registry


# Type annotations for endpoint signatures
TaskManagerDep = Annotated[TaskExecutionManager, Depends(get_task_manager)]
WorkerManagerDep = Annotated[WorkerManager, Depends(get_worker_manager)]
EventBusDep = Annotated[EventBus, Depends(get_event_bus)]
HandlerRegistryDep = Annotated[HandlerRegistry, Depends(get_handler_registry)]
AuthDep = Annotated[AuthContext, Depends(require_auth)]
