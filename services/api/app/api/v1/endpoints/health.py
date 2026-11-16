"""Health check endpoint."""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.system import HealthResponse
from app.services.service_container import get_container

router = APIRouter(tags=["system"])


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Returns actual service health, uptime, and configuration safety."""
    container = get_container()
    return HealthResponse(
        status="healthy" if container.is_ready else "degraded",
        version=settings.app_version,
        uptime_seconds=container.uptime_seconds,
        environment=settings.environment,
        is_loopback=settings.is_loopback,
    )
