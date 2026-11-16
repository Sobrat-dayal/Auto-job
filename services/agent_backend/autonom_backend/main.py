"""FastAPI application main entry point for the AUTONOM agent backend."""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from autonom_backend import __version__
from autonom_backend.config import settings
from autonom_backend.db.database import db_manager
from autonom_backend.api.health import router as health_router
from autonom_backend.api.system import router as system_router
from autonom_backend.api.agents import router as agents_router
from autonom_backend.api.jobs import router as jobs_router
from autonom_backend.api.governance import router as governance_router

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger("autonom_backend")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager for startup and shutdown routines."""
    logger.info(f"Starting {settings.app_name} v{__version__}...")
    # Initialize SQLite database with WAL mode and schema tables
    await db_manager.initialize()
    yield
    logger.info("Shutting down AUTONOM agent backend.")


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="Autonomous Agent Backend for Job Discovery, Resume Tailoring, Computer Use, and Multi-Agent Swarms.",
    lifespan=lifespan,
)

# CORS configuration for desktop and webview clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(health_router)
app.include_router(system_router)
app.include_router(agents_router)
app.include_router(jobs_router)
app.include_router(governance_router)


@app.get("/")
async def root():
    return {
        "app": settings.app_name,
        "version": __version__,
        "status": "operational",
        "docs_url": "/docs",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "autonom_backend.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
    )
