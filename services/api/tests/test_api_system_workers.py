"""Integration tests for worker pool and system diagnostics endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_workers_endpoint(async_client: AsyncClient, auth_headers: dict[str, str]):
    response = await async_client.get("/api/v1/workers", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "total_workers" in data
    assert "active_workers" in data
    assert "workers" in data
    assert len(data["workers"]) == data["total_workers"]


@pytest.mark.asyncio
async def test_system_status_endpoint(async_client: AsyncClient, auth_headers: dict[str, str]):
    response = await async_client.get("/api/v1/system/status", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "uptime_seconds" in data
    assert "active_tasks" in data
    assert "queued_tasks" in data
    assert "workers" in data


@pytest.mark.asyncio
async def test_system_capabilities_endpoint(async_client: AsyncClient, auth_headers: dict[str, str]):
    response = await async_client.get("/api/v1/system/capabilities", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "task_execution" in data["capabilities"]
    assert "compute.echo" in data["supported_task_types"]
    assert "test.sleep_progress" in data["supported_task_types"]
    assert data["realtime_streaming"] is True


@pytest.mark.asyncio
async def test_system_endpoints_unauthenticated(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/system/status")
    assert resp.status_code == 401
    assert resp.json()["error"]["code"] == "UNAUTHENTICATED"
