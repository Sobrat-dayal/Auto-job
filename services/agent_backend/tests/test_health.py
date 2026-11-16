"""Tests for health, root, and system telemetry endpoints."""

import pytest
from httpx import AsyncClient, ASGITransport
from autonom_backend.main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "operational"
        assert "version" in data
        assert data["app"] == "AUTONOM Agent Backend"


@pytest.mark.asyncio
async def test_health_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] in ("healthy", "degraded")
        assert data["database"]["connected"] is True
        assert data["database"]["mode"].lower() == "wal"
        assert "uptime_seconds" in data
        assert data["subsystems"]["agent_engine"] == "ready"


@pytest.mark.asyncio
async def test_system_endpoint():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/system")
        assert response.status_code == 200
        data = response.json()
        assert "os" in data
        assert "cpu_usage_percent" in data
        assert "memory" in data
        assert data["memory"]["total_mb"] > 0
        assert data["memory"]["process_rss_mb"] > 0
        assert len(data["monitors"]) >= 1
