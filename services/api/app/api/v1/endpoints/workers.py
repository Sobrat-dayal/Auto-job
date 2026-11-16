"""Worker pool status and observability endpoints."""

from fastapi import APIRouter

from app.api.dependencies import AuthDep, WorkerManagerDep
from app.schemas.system import WorkerListResponse

router = APIRouter(prefix="/workers", tags=["workers"])


@router.get("", response_model=WorkerListResponse)
async def get_workers(
    worker_manager: WorkerManagerDep,
    _auth: AuthDep,
) -> WorkerListResponse:
    """Returns the operational status, capacity, and task allocations of the background worker pool."""
    return worker_manager.get_status()
