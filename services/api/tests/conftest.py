"""Shared pytest fixtures for the AUTONOM API test suite."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import app
from app.services.service_container import reset_container


@pytest.fixture(autouse=True)
async def initialized_container():
    """Initializes a fresh backend service container before each test and shuts down after."""
    container = reset_container()
    await container.initialize()
    yield container
    await container.shutdown()


@pytest.fixture
async def async_client():
    """Async HTTP client bound to the FastAPI application with ASGITransport."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def auth_headers() -> dict[str, str]:
    """Standard authentication headers for protected endpoint requests."""
    return {"Authorization": f"Bearer {settings.api_key}"}
