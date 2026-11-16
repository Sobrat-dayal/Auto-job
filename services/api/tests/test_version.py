"""Tests for /api/v1/version endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_version_endpoint_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/version")
        assert response.status_code == 200
        data = response.json()
        assert data["app_name"] == "AUTONOM API"
        assert data["version"] == "0.1.0"
        assert data["api_version"] == "v1"
        assert "python_version" in data
        assert "platform" in data
