"""Integration tests for the /api/v1/dashboard aggregate REST endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_dashboard_overview_unauthenticated(async_client: AsyncClient):
    response = await async_client.get("/api/v1/dashboard/overview")
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


@pytest.mark.asyncio
async def test_dashboard_overview_authenticated(async_client: AsyncClient, auth_headers: dict[str, str]):
    response = await async_client.get("/api/v1/dashboard/overview", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()

    # System status
    assert data["system_status"] in ("operational", "degraded")
    assert data["backend_connected"] is True
    assert "uptime_seconds" in data
    assert data["task_dispatch_status"] == "active"
    assert data["ai_swarm_status"] == "scheduled_stage_12"

    # Tasks summary
    tasks_summary = data["tasks_summary"]
    assert "running" in tasks_summary
    assert "queued" in tasks_summary
    assert "completed" in tasks_summary
    assert "failed" in tasks_summary
    assert "total" in tasks_summary

    # Agents list (3 prominent agents, explicitly unavailable in Stage 08)
    agents = data["agents"]
    assert len(agents) == 3
    agent_ids = [a["id"] for a in agents]
    assert "job-discovery-agent" in agent_ids
    assert "application-agent" in agent_ids
    assert "supervisor-agent" in agent_ids
    for a in agents:
        assert a["is_available"] is False
        assert a["status"] == "unavailable"

    # Recruitment summary
    recruitment = data["recruitment"]
    assert "jobs_discovered" in recruitment
    assert "applications_total" in recruitment
    assert "pipeline_stages" in recruitment
    assert recruitment["automated_scouting_enabled"] is False

    # Workers
    assert "workers" in data
    assert "total" in data["workers"]


@pytest.mark.asyncio
async def test_dashboard_task_trends(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Unauthenticated check
    unauth = await async_client.get("/api/v1/dashboard/task-trends")
    assert unauth.status_code == 401

    # 2. Authenticated query for 7d
    res_7d = await async_client.get("/api/v1/dashboard/task-trends?window=7d", headers=auth_headers)
    assert res_7d.status_code == 200
    data_7d = res_7d.json()
    assert data_7d["window"] == "7d"
    assert len(data_7d["data_points"]) == 7
    assert "total_volume" in data_7d
    assert "overall_success_rate" in data_7d

    # 3. Authenticated query for today
    res_today = await async_client.get("/api/v1/dashboard/task-trends?window=today", headers=auth_headers)
    assert res_today.status_code == 200
    assert len(res_today.json()["data_points"]) == 1

    # 4. Authenticated query for 30d
    res_30d = await async_client.get("/api/v1/dashboard/task-trends?window=30d", headers=auth_headers)
    assert res_30d.status_code == 200
    assert len(res_30d.json()["data_points"]) == 30


@pytest.mark.asyncio
async def test_dashboard_activity(async_client: AsyncClient, auth_headers: dict[str, str]):
    # Unauthenticated
    unauth = await async_client.get("/api/v1/dashboard/activity")
    assert unauth.status_code == 401

    # Authenticated
    res = await async_client.get("/api/v1/dashboard/activity?limit=20", headers=auth_headers)
    assert res.status_code == 200
    events = res.json()
    assert isinstance(events, list)
