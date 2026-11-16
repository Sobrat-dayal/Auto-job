"""System diagnostics and capabilities endpoints."""

from fastapi import APIRouter

from app.api.dependencies import AuthDep, ContainerDep, HandlerRegistryDep
from app.core.config import settings
from app.schemas.system import SystemCapabilitiesResponse, SystemStatusResponse

router = APIRouter(prefix="/system", tags=["system"])


@router.get("/status", response_model=SystemStatusResponse)
async def get_system_status(
    container: ContainerDep,
    _auth: AuthDep,
) -> SystemStatusResponse:
    """Returns runtime operational metrics including queue depth, active tasks, and worker loads."""
    status_data = container.get_system_status()
    return SystemStatusResponse(**status_data)


@router.get("/capabilities", response_model=SystemCapabilitiesResponse)
async def get_system_capabilities(
    handler_registry: HandlerRegistryDep,
    _auth: AuthDep,
) -> SystemCapabilitiesResponse:
    """Returns currently implemented backend capabilities and registered task handlers."""
    return SystemCapabilitiesResponse(
        capabilities=[
            "task_execution",
            "bounded_worker_concurrency",
            "event_streaming_sse",
            "in_memory_event_bus",
            "cooperative_cancellation",
            "task_state_machine",
            "local_token_auth",
        ],
        supported_task_types=handler_registry.list_types(),
        max_concurrency=settings.max_concurrent_workers,
        max_queue_size=settings.max_queued_tasks,
        realtime_streaming=True,
    )
