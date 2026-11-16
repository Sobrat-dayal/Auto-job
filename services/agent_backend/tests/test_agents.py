"""Tests for agent swarm queries and task dispatching."""

import pytest
from httpx import AsyncClient, ASGITransport
from autonom_backend.main import app
from autonom_backend.db.database import db_manager


@pytest.mark.asyncio
async def test_list_agents():
    await db_manager.initialize()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/agents")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) >= 4
        assert "total_active_tasks" in data


@pytest.mark.asyncio
async def test_dispatch_task_success():
    await db_manager.initialize()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "task_type": "job_search",
            "parameters": {"keywords": ["Rust", "Python"], "location": "Remote"},
            "priority": "high",
        }
        response = await client.post("/api/agents/scout-01/dispatch", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "queued"
        assert data["assigned_agent"] == "scout-01"
        assert data["task_id"].startswith("tsk_")


@pytest.mark.asyncio
async def test_dispatch_task_invalid_agent():
    await db_manager.initialize()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "task_type": "job_search",
            "parameters": {},
        }
        response = await client.post("/api/agents/non-existent-agent-id/dispatch", json=payload)
        assert response.status_code == 404
