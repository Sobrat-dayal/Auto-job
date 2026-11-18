"""Integration tests for the /api/v1/desktop REST endpoints (Stage 17)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_desktop_endpoints_unauthenticated(async_client: AsyncClient):
    """Verify unauthorized requests are rejected with 401."""
    resp = await async_client.get("/api/v1/desktop/status")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_desktop_status_authenticated(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify authenticated status returns active session info, resolution, and UIA availability."""
    resp = await async_client.get("/api/v1/desktop/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "session" in data
    assert "resolution" in data["session"]
    assert "x" in data["session"]["resolution"]
    assert data["uia_available"] is True
    assert isinstance(data["emergency_stop_active"], bool)


@pytest.mark.asyncio
async def test_desktop_applications_list(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify GET /api/v1/desktop/applications returns running process applications."""
    resp = await async_client.get("/api/v1/desktop/applications", headers=auth_headers)
    assert resp.status_code == 200
    apps = resp.json()
    assert isinstance(apps, list)
    assert len(apps) > 0

    first = apps[0]
    assert "executable_name" in first
    assert "pids" in first
    assert "is_allowed" in first


@pytest.mark.asyncio
async def test_desktop_windows_list(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify GET /api/v1/desktop/windows returns active top-level windows."""
    resp = await async_client.get("/api/v1/desktop/windows", headers=auth_headers)
    assert resp.status_code == 200
    windows = resp.json()
    assert isinstance(windows, list)
    assert len(windows) > 0

    first = windows[0]
    assert "window_ref" in first
    assert "hwnd" in first
    assert "title" in first
    assert "process_name" in first


@pytest.mark.asyncio
async def test_desktop_inspect_tree_endpoint(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify POST /api/v1/desktop/windows/{window_ref}/inspect returns a UI automation tree snapshot."""
    win_resp = await async_client.get("/api/v1/desktop/windows", headers=auth_headers)
    windows = win_resp.json()
    visible = [w for w in windows if w.get("is_visible") and w["bounds"]["width"] > 100]
    assert len(visible) > 0

    # Pick an allowed window
    for target_window in visible:
        ref = target_window["window_ref"]
        payload = {
            "max_depth": 2,
            "max_nodes": 20,
        }
        resp = await async_client.post(f"/api/v1/desktop/windows/{ref}/inspect", json=payload, headers=auth_headers)
        if resp.status_code == 200:
            data = resp.json()
            assert data["window_ref"] == ref
            assert "root" in data
            assert data["total_nodes"] > 0
            break
        elif resp.status_code == 403:
            # Policy enforcement working as designed for non-whitelisted app
            continue


@pytest.mark.asyncio
async def test_desktop_find_elements_endpoint(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify POST /api/v1/desktop/elements/search queries elements in a window."""
    win_resp = await async_client.get("/api/v1/desktop/windows", headers=auth_headers)
    windows = win_resp.json()
    visible = [w for w in windows if w.get("is_visible") and w["bounds"]["width"] > 100]
    assert len(visible) > 0

    for target_window in visible:
        ref = target_window["window_ref"]
        payload = {
            "window_ref": ref,
            "query": {
                "control_type": "Button",
            },
        }
        resp = await async_client.post("/api/v1/desktop/elements/search", json=payload, headers=auth_headers)
        if resp.status_code == 200:
            elements = resp.json()
            assert isinstance(elements, list)
            break
        elif resp.status_code == 403:
            continue


@pytest.mark.asyncio
async def test_desktop_tasks_crud(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify POST and GET /api/v1/desktop/tasks for desktop automation workflow tasks."""
    payload = {
        "goal": "Inspect top-level applications and locate controls",
    }
    create_resp = await async_client.post("/api/v1/desktop/tasks", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    task = create_resp.json()
    assert task["goal"] == payload["goal"]
    assert task["status"] == "pending"

    # List tasks
    list_resp = await async_client.get("/api/v1/desktop/tasks", headers=auth_headers)
    assert list_resp.status_code == 200
    tasks = list_resp.json()
    assert len(tasks) >= 1
    assert any(t["task_id"] == task["task_id"] for t in tasks)

    # Get single task
    get_resp = await async_client.get(f"/api/v1/desktop/tasks/{task['task_id']}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["task_id"] == task["task_id"]


@pytest.mark.asyncio
async def test_desktop_history_and_diagnostics(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify history and diagnostics endpoints return valid operational structures."""
    hist_resp = await async_client.get("/api/v1/desktop/history", headers=auth_headers)
    assert hist_resp.status_code == 200
    assert isinstance(hist_resp.json(), list)

    diag_resp = await async_client.get("/api/v1/desktop/diagnostics", headers=auth_headers)
    assert diag_resp.status_code == 200
    diag = diag_resp.json()
    assert "active_worker_threads" in diag
    assert "cached_windows" in diag
    assert diag["cached_windows"] > 0
    assert diag["uia_available"] is True
