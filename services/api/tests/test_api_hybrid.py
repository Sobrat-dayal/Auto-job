"""Integration tests for the /api/v1/hybrid REST endpoints (Stage 19)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_hybrid_unauthenticated_rejected(async_client: AsyncClient) -> None:
    """Verify unauthorized requests to /api/v1/hybrid/* are rejected with 401."""
    resp = await async_client.get("/api/v1/hybrid/status")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_hybrid_status_and_methods(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Verify engine status and registered methods list."""
    status_resp = await async_client.get("/api/v1/hybrid/status", headers=auth_headers)
    assert status_resp.status_code == 200
    status_data = status_resp.json()
    assert status_data["status"] == "operational"
    assert "BROWSER_DOM" in status_data["methods_available"]
    assert "WINDOWS_UIA" in status_data["methods_available"]
    assert "VISUAL_GROUNDING" in status_data["methods_available"]

    methods_resp = await async_client.get("/api/v1/hybrid/methods", headers=auth_headers)
    assert methods_resp.status_code == 200
    methods_data = methods_resp.json()
    assert "BROWSER_DOM" in methods_data
    assert "WINDOWS_UIA" in methods_data
    assert "VISUAL_GROUNDING" in methods_data


@pytest.mark.asyncio
async def test_hybrid_capabilities(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Verify capability metadata endpoint."""
    resp = await async_client.get("/api/v1/hybrid/capabilities", headers=auth_headers)
    assert resp.status_code == 200
    caps = resp.json()
    assert len(caps) >= 4
    method_names = [c["method"] for c in caps]
    assert "BROWSER_DOM" in method_names
    assert "WINDOWS_UIA" in method_names


@pytest.mark.asyncio
async def test_hybrid_resolve_target(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Verify target resolution from DOM and window hints."""
    resp = await async_client.post(
        "/api/v1/hybrid/targets/resolve",
        json={"target_hint": "button#submit", "dom_selector": "button#submit"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["surface_type"] == "BROWSER_DOM"
    assert data["dom_selector"] == "button#submit"


@pytest.mark.asyncio
async def test_hybrid_route_preview(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Verify explainable route simulation endpoint without executing actions."""
    target_payload = {
        "target_type": "BROWSER_ELEMENT",
        "surface_type": "BROWSER_DOM",
        "dom_selector": "button.primary",
    }
    resp = await async_client.post(
        "/api/v1/hybrid/route/preview",
        json={"target": target_payload, "action_type": "click"},
        headers=auth_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["selected_method"] == "BROWSER_DOM"
    assert "rationale" in data
    assert "scoring" in data


@pytest.mark.asyncio
async def test_hybrid_actions_and_get(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Verify action dispatch, verification, and retrieval."""
    action_payload = {
        "target": {
            "target_type": "BROWSER_ELEMENT",
            "surface_type": "BROWSER_DOM",
            "dom_selector": "button#ok",
        },
        "action_type": "click",
        "allow_fallback": True,
    }
    resp = await async_client.post("/api/v1/hybrid/actions", json=action_payload, headers=auth_headers)
    assert resp.status_code == 200
    res_data = resp.json()
    action_id = res_data["action_id"]
    assert res_data["method"] in ("BROWSER_DOM", "WINDOWS_UIA", "VISUAL_GROUNDING")

    # Get action
    get_resp = await async_client.get(f"/api/v1/hybrid/actions/{action_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["action_id"] == action_id


@pytest.mark.asyncio
async def test_hybrid_task_submission_and_lifecycle(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Verify submitting a hybrid task and checking its status."""
    task_payload = {
        "instruction": "Click the submit button on application form",
        "action_type": "click",
        "allow_fallback": True,
    }
    submit_resp = await async_client.post("/api/v1/hybrid/tasks", json=task_payload, headers=auth_headers)
    assert submit_resp.status_code == 200
    task_data = submit_resp.json()
    task_id = task_data["task_id"]
    assert task_data["status"] in ("completed", "failed")

    # Get task
    get_resp = await async_client.get(f"/api/v1/hybrid/tasks/{task_id}", headers=auth_headers)
    assert get_resp.status_code == 200
    assert get_resp.json()["task_id"] == task_id

    # List tasks
    list_resp = await async_client.get("/api/v1/hybrid/tasks?limit=10", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()) >= 1


@pytest.mark.asyncio
async def test_hybrid_diagnostics_and_killswitch(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Verify diagnostics telemetry and killswitch trigger/reset."""
    diag_resp = await async_client.get("/api/v1/hybrid/diagnostics", headers=auth_headers)
    assert diag_resp.status_code == 200
    diag_data = diag_resp.json()
    assert diag_data["engine_version"] == "1.0.0"
    assert "methods" in diag_data

    # Activate killswitch
    act_resp = await async_client.post(
        "/api/v1/hybrid/killswitch/activate",
        json={"reason": "Integration test killswitch"},
        headers=auth_headers,
    )
    assert act_resp.status_code == 200
    assert act_resp.json()["status"] == "activated"

    # Action should now be blocked by emergency stop
    blocked_resp = await async_client.post(
        "/api/v1/hybrid/actions",
        json={
            "target": {"target_type": "BROWSER_PAGE", "surface_type": "BROWSER_DOM"},
            "action_type": "click",
        },
        headers=auth_headers,
    )
    assert blocked_resp.status_code == 423

    # Reset killswitch
    deact_resp = await async_client.post("/api/v1/hybrid/killswitch/deactivate", headers=auth_headers)
    assert deact_resp.status_code == 200
    assert deact_resp.json()["status"] == "deactivated"
