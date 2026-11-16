"""Integration test verifying task persistence across service restart."""

from pathlib import Path

import pytest
from httpx import ASGITransport, AsyncClient

from app.core.config import settings
from app.main import app
from app.services.service_container import reset_container


@pytest.mark.asyncio
async def test_task_persistence_across_restart(tmp_path: Path, monkeypatch):
    data_dir = tmp_path / "appdata"
    monkeypatch.setattr(settings, "data_dir", data_dir)
    settings.ensure_directories()

    # 1. Start Server Instance 1
    container1 = reset_container()
    await container1.initialize()

    transport = ASGITransport(app=app)
    headers = {"Authorization": f"Bearer {settings.api_key}"}

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create and execute echo task
        create_res = await client.post(
            "/api/v1/tasks",
            json={"task_type": "compute.echo", "payload": {"text": "PersistMe", "repeat": 1}},
            headers=headers,
        )
        assert create_res.status_code == 201
        task_id = create_res.json()["task_id"]

        # Wait a moment for execution to complete
        import asyncio

        await asyncio.sleep(0.3)

        res = await client.get(f"/api/v1/tasks/{task_id}", headers=headers)
        assert res.status_code == 200
        assert res.json()["state"] == "Completed"

    # 2. Stop Server Instance 1 (clean shutdown)
    await container1.shutdown()

    # 3. Start Server Instance 2 (simulate process restart)
    container2 = reset_container()
    await container2.initialize()

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Query task created by previous server process
        res2 = await client.get(f"/api/v1/tasks/{task_id}", headers=headers)
        assert res2.status_code == 200
        task_data = res2.json()
        assert task_data["task_id"] == task_id
        assert task_data["state"] == "Completed"
        assert task_data["progress"] == 100.0

        # Query durable event history
        hist_res = await client.get(f"/api/v1/tasks/{task_id}/history", headers=headers)
        assert hist_res.status_code == 200
        history = hist_res.json()
        assert len(history) >= 3
        event_types = [h["event_type"] for h in history]
        assert "task.created" in event_types
        assert "task.completed" in event_types

    await container2.shutdown()
