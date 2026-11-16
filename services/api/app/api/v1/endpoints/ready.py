"""Readiness check endpoint."""

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.system import ReadinessResponse
from app.services.service_container import get_container

router = APIRouter(tags=["system"])


@router.get("/ready", response_model=ReadinessResponse)
async def get_readiness() -> ReadinessResponse:
    """Returns whether the API service is initialized and ready to accept requests."""
    container = get_container()
    checks = {
        "api_router": True,
        "config_loaded": bool(settings.app_name),
        "data_dir_accessible": settings.data_dir.parent.exists(),
        **container.get_readiness_checks(),
    }
    all_ready = all(checks.values())

    return ReadinessResponse(
        ready=all_ready,
        status="ready" if all_ready else "not_ready",
        checks=checks,
    )
