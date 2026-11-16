"""Integration tests for the /api/v1/tasks REST endpoints."""

import asyncio

import pytest
from httpx import AsyncClient

from app.schemas.tasks import TaskState


@pytest.mark.asyncio
async def test_create_task_unauthenticated(async_client: AsyncClient):
    response = await async_client.post(
        "/api/v1/tasks",
        json={"task_type": "compute.echo", "payload": {"text": "hello"}},
    )
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHENTICATED"


@pytest.mark.asyncio
async def test_create_and_query_task_success(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Create task
    response = await async_client.post(
        "/api/v1/tasks",
        json={"task_type": "compute.echo", "payload": {"text": "AUTONOM", "repeat": 1}},
        headers=auth_headers,
    )
    assert response.status_code == 201
    task_data = response.json()
    task_id = task_data["task_id"]
    assert task_data["task_type"] == "compute.echo"

    # 2. Get task by ID
    get_resp = await async_client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["task_id"] == task_id

    # 3. List tasks
    list_resp = await async_client.get("/api/v1/tasks", headers=auth_headers)
    assert list_resp.status_code == 200
    list_data = list_resp.json()
    assert list_data["total"] >= 1
    assert any(t["task_id"] == task_id for t in list_data["tasks"])

    # 4. Wait for completion and check result
    for _ in range(40):
        await asyncio.sleep(0.05)
        res_poll = await async_client.get(f"/api/v1/tasks/{task_id}", headers=auth_headers)
        if res_poll.json()["state"] == TaskState.COMPLETED.value:
            break

    result_resp = await async_client.get(f"/api/v1/tasks/{task_id}/result", headers=auth_headers)
    assert result_resp.status_code == 200
    result_data = result_resp.json()
    assert result_data["state"] == TaskState.COMPLETED.value
    assert result_data["result"] is not None


@pytest.mark.asyncio
async def test_cancel_task_endpoint(async_client: AsyncClient, auth_headers: dict[str, str]):
    create_resp = await async_client.post(
        "/api/v1/tasks",
        json={"task_type": "test.sleep_progress", "payload": {"steps": 10, "step_delay": 0.2}},
        headers=auth_headers,
    )
    assert create_resp.status_code == 201
    task_id = create_resp.json()["task_id"]

    await asyncio.sleep(0.05)
    cancel_resp = await async_client.post(
        f"/api/v1/tasks/{task_id}/cancel",
        headers=auth_headers,
    )
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["cancelled"] is True


@pytest.mark.asyncio
async def test_get_nonexistent_task_returns_404(async_client: AsyncClient, auth_headers: dict[str, str]):
    response = await async_client.get("/api/v1/tasks/tsk-notfound", headers=auth_headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "TASK_NOT_FOUND"
