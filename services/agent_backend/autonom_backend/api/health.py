"""Health check and diagnostic endpoints for AUTONOM backend."""

import time
from fastapi import APIRouter
from autonom_backend import __version__
from autonom_backend.db.database import db_manager

router = APIRouter(prefix="/api/health", tags=["health"])

_START_TIME = time.time()


@router.get("")
async def get_health():
    """Returns the operational status of the backend service and subsystems."""
    uptime = time.time() - _START_TIME
    db_health = await db_manager.check_health()

    return {
        "status": "healthy" if db_health.get("connected") else "degraded",
        "version": __version__,
        "uptime_seconds": round(uptime, 2),
        "database": db_health,
        "subsystems": {
            "agent_engine": "ready",
            "computer_interaction": "ready",
            "job_crawler": "idle",
        },
    }
