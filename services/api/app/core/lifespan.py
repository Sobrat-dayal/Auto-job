"""FastAPI application lifespan context manager for startup and shutdown execution."""

import logging
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging
from app.services.service_container import get_container

logger = logging.getLogger("autonom.lifecycle")


@asynccontextmanager
async def application_lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Sequential service initialization and controlled shutdown lifecycle."""
    setup_logging(settings.log_level)
    logger.info(f"Starting {settings.app_name} v{settings.app_version} in {settings.environment} mode...")
    logger.info(f"Binding to {settings.host}:{settings.port} (Loopback: {settings.is_loopback})")

    container = get_container()
    await container.initialize()

    yield

    logger.info("Initiating service shutdown...")
    await container.shutdown()
    logger.info(f"{settings.app_name} shutdown cleanly.")
