"""API v1 router definition aggregating all versioned endpoints."""

from fastapi import APIRouter

from app.api.v1.endpoints.agents import router as agents_router
from app.api.v1.endpoints.ai import router as ai_router
from app.api.v1.endpoints.applications import router as applications_router
from app.api.v1.endpoints.artifacts import router as artifacts_router
from app.api.v1.endpoints.browser import router as browser_router
from app.api.v1.endpoints.credentials import router as credentials_router
from app.api.v1.endpoints.dashboard import router as dashboard_router
from app.api.v1.endpoints.desktop import router as desktop_router
from app.api.v1.endpoints.events import router as events_router
from app.api.v1.endpoints.health import router as health_router
from app.api.v1.endpoints.hybrid import router as hybrid_router
from app.api.v1.endpoints.integrations import router as integrations_router
from app.api.v1.endpoints.jobs import router as jobs_router
from app.api.v1.endpoints.orchestration import router as orchestration_router
from app.api.v1.endpoints.memory import router as memory_router
from app.api.v1.endpoints.profiles import router as profiles_router
from app.api.v1.endpoints.ready import router as ready_router
from app.api.v1.endpoints.security import router as security_router
from app.api.v1.endpoints.settings import router as settings_router
from app.api.v1.endpoints.storage import router as storage_router
from app.api.v1.endpoints.system import router as system_router
from app.api.v1.endpoints.tasks import router as tasks_router
from app.api.v1.endpoints.version import router as version_router
from app.api.v1.endpoints.visual import router as visual_router
from app.api.v1.endpoints.workers import router as workers_router

api_v1_router = APIRouter(prefix="/api/v1")

# System probes (unauthenticated)
api_v1_router.include_router(health_router)
api_v1_router.include_router(ready_router)
api_v1_router.include_router(version_router)

# Operational endpoints (authenticated)
api_v1_router.include_router(tasks_router)
api_v1_router.include_router(workers_router)
api_v1_router.include_router(system_router)
api_v1_router.include_router(events_router)
api_v1_router.include_router(storage_router)
api_v1_router.include_router(settings_router)
api_v1_router.include_router(profiles_router)
api_v1_router.include_router(credentials_router)
api_v1_router.include_router(integrations_router)
api_v1_router.include_router(dashboard_router)
api_v1_router.include_router(jobs_router)
api_v1_router.include_router(applications_router)
api_v1_router.include_router(artifacts_router)
api_v1_router.include_router(ai_router)
api_v1_router.include_router(agents_router)
api_v1_router.include_router(orchestration_router)
api_v1_router.include_router(security_router)
api_v1_router.include_router(memory_router)
api_v1_router.include_router(browser_router)
api_v1_router.include_router(desktop_router)
api_v1_router.include_router(visual_router)
api_v1_router.include_router(hybrid_router)
