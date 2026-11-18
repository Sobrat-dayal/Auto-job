"""Integration tests for the /api/v1/visual REST endpoints (Stage 18)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_visual_endpoints_unauthenticated(async_client: AsyncClient):
    """Verify unauthorized requests are rejected with 401."""
    resp = await async_client.get("/api/v1/visual/diagnostics")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_visual_diagnostics(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify GET /api/v1/visual/diagnostics returns hardware capture providers, monitors, and OCR status."""
    resp = await async_client.get("/api/v1/visual/diagnostics", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert "active_provider" in data
    assert "available_providers" in data
    assert "monitors_count" in data
    assert data["monitors_count"] >= 1
    assert "offline_windows_ocr_available" in data
    assert isinstance(data["offline_windows_ocr_available"], bool)


@pytest.mark.asyncio
async def test_visual_monitors(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify GET /api/v1/visual/monitors returns all connected physical monitors."""
    resp = await async_client.get("/api/v1/visual/monitors", headers=auth_headers)
    assert resp.status_code == 200
    monitors = resp.json()
    assert isinstance(monitors, list)
    assert len(monitors) >= 1
    first = monitors[0]
    assert "display_index" in first
    assert "width" in first
    assert "height" in first
    assert "scale_factor" in first


@pytest.mark.asyncio
async def test_visual_session_lifecycle(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify creating, inspecting, capturing from, and closing a capture session via REST."""
    # Create
    resp = await async_client.post(
        "/api/v1/visual/sessions",
        json={"target_type": "display", "display_index": 0, "provider": "mss"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    sess = resp.json()
    sess_id = sess["session_id"]
    assert sess_id.startswith("vsess_")

    # List sessions
    list_resp = await async_client.get("/api/v1/visual/sessions", headers=auth_headers)
    assert list_resp.status_code == 200
    assert any(s["session_id"] == sess_id for s in list_resp.json())

    # Capture frame
    frame_resp = await async_client.post(f"/api/v1/visual/sessions/{sess_id}/frame", headers=auth_headers)
    assert frame_resp.status_code == 200
    frame_data = frame_resp.json()
    assert "frame_id" in frame_data
    assert "thumbnail_b64" in frame_data
    assert len(frame_data["thumbnail_b64"]) > 50

    # Detect elements
    el_resp = await async_client.post(f"/api/v1/visual/sessions/{sess_id}/detect-elements", headers=auth_headers)
    assert el_resp.status_code == 200
    assert isinstance(el_resp.json(), list)

    # Close session
    del_resp = await async_client.delete(f"/api/v1/visual/sessions/{sess_id}", headers=auth_headers)
    assert del_resp.status_code == 200
    assert del_resp.json()["closed"] is True


@pytest.mark.asyncio
async def test_visual_tasks(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify submitting and listing visual computer tasks."""
    resp = await async_client.post(
        "/api/v1/visual/tasks",
        json={"instruction": "Find screen elements and verify", "display_index": 0},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    task_data = resp.json()
    assert "task_id" in task_data
    assert "status" in task_data

    # List tasks
    list_resp = await async_client.get("/api/v1/visual/tasks", headers=auth_headers)
    assert list_resp.status_code == 200
    assert any(t["task_id"] == task_data["task_id"] for t in list_resp.json())


@pytest.mark.asyncio
async def test_visual_recovery_events(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verify GET /api/v1/visual/recovery-events returns recovery history."""
    resp = await async_client.get("/api/v1/visual/recovery-events", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
