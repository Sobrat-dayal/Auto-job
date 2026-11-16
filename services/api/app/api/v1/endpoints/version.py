"""Version information endpoint."""

import platform
import sys

from fastapi import APIRouter

from app.core.config import settings
from app.schemas.system import VersionResponse

router = APIRouter(tags=["system"])


@router.get("/version", response_model=VersionResponse)
async def get_version() -> VersionResponse:
    """Returns application version, API version, and runtime platform."""
    return VersionResponse(
        app_name=settings.app_name,
        version=settings.app_version,
        api_version="v1",
        python_version=platform.python_version(),
        platform=sys.platform,
    )
