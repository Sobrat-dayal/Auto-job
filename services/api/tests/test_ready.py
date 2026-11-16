"""Tests for /api/v1/ready endpoint."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_readiness_endpoint_success():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/ready")
        assert response.status_code == 200
        data = response.json()
        assert data["ready"] is True
        assert data["status"] == "ready"
        assert "checks" in data
        assert data["checks"]["api_router"] is True
        assert data["checks"]["config_loaded"] is True
