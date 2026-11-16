"""FastAPI Application Entry Point for AUTONOM API Service."""

import logging
from uuid import uuid4

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.errors import register_exception_handlers
from app.api.v1.endpoints.health import get_health
from app.api.v1.router import api_v1_router
from app.core.config import settings
from app.core.lifespan import application_lifespan
from app.schemas.system import HealthResponse

logger = logging.getLogger("autonom.api")


class CorrelationIdMiddleware:
    """Pure ASGI middleware assigning or propagating correlation IDs without buffering streaming bodies."""

    def __init__(self, app) -> None:
        self.app = app

    async def __call__(self, scope, receive, send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        req_id = None
        for name, value in scope.get("headers", []):
            if name.lower() == b"x-request-id":
                req_id = value.decode("latin1")
                break
        if not req_id:
            req_id = f"req-{uuid4().hex[:8]}"

        # Propagate request_id into state
        scope.setdefault("state", {})["request_id"] = req_id

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                headers = list(message.get("headers", []))
                headers.append((b"x-request-id", req_id.encode("latin1")))
                message["headers"] = headers
            await send(message)

        await self.app(scope, receive, send_wrapper)


def create_app() -> FastAPI:
    """Factory creating and configuring the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version=settings.app_version,
        description="AUTONOM Autonomous Desktop Assistant API Service",
        lifespan=application_lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Middleware: CORS configuration
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
        allow_headers=["*"],
    )

    # Register centralized exception handlers
    register_exception_handlers(app)

    # Include versioned API routers
    app.include_router(api_v1_router)

    # Alias /api/health to canonical /api/v1/health for backward compatibility
    @app.get("/api/health", response_model=HealthResponse, tags=["system"], include_in_schema=False)
    async def legacy_health_alias():
        return await get_health()

    # Root endpoint
    @app.get("/", tags=["root"])
    async def root():
        return {
            "app": settings.app_name,
            "version": settings.app_version,
            "status": "operational",
            "api_v1": "/api/v1",
            "docs": "/docs",
        }

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
