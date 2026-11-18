"""Integration tests for the /api/v1/reliability REST endpoints (Stage 20)."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_reliability_unauthenticated_rejected(async_client: AsyncClient) -> None:
    """Verify unauthorized requests to /api/v1/reliability/* are rejected with 401."""
    resp = await async_client.get("/api/v1/reliability/diagnostics")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_reliability_diagnostics(async_client: AsyncClient, auth_headers: dict[str, str]) -> None:
    """Verify reliability diagnostics status endpoint."""
    resp = await async_client.get("/api/v1/reliability/diagnostics", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["service_status"] == "operational"
    assert "active_recording_sessions" in data
    assert "total_registered_procedures" in data


@pytest.mark.asyncio
async def test_recording_and_procedure_api_lifecycle(
    async_client: AsyncClient, auth_headers: dict[str, str]
) -> None:
    """Verify recording creation, action logging, stopping, compilation, and execution."""
    # 1. Start recording
    start_resp = await async_client.post(
        "/api/v1/reliability/recordings",
        headers=auth_headers,
        json={
            "name": "Integration Test Recording",
            "allowed_app_scopes": ["notepad.exe"],
            "allowed_web_origins": ["https://jobs.example.com"],
        },
    )
    assert start_resp.status_code == 201
    session = start_resp.json()
    session_id = session["session_id"]
    assert session["status"] == "active"

    # 2. Record an action
    action_resp = await async_client.post(
        f"/api/v1/reliability/recordings/{session_id}/actions",
        headers=auth_headers,
        json={
            "source_adapter": "desktop",
            "action_type": "type_text",
            "raw_parameters": {"text": "Integration test query"},
            "application_name": "notepad.exe",
        },
    )
    assert action_resp.status_code == 201
    action = action_resp.json()
    assert action["sequence_number"] == 1

    # 3. Stop recording
    stop_resp = await async_client.post(
        f"/api/v1/reliability/recordings/{session_id}/stop",
        headers=auth_headers,
    )
    assert stop_resp.status_code == 200
    stopped = stop_resp.json()
    assert stopped["status"] == "stopped"
    assert stopped["integrity_hash"] is not None

    # 4. Compile procedure
    compile_resp = await async_client.post(
        "/api/v1/reliability/procedures/compile",
        headers=auth_headers,
        json={
            "session_id": session_id,
            "name": "Notepad Typing Procedure",
            "parameterize_inputs": True,
        },
    )
    assert compile_resp.status_code == 201
    proc = compile_resp.json()
    proc_id = proc["procedure_id"]
    assert proc["version"] == 1
    assert len(proc["steps"]) == 1

    # 5. List procedures
    list_resp = await async_client.get("/api/v1/reliability/procedures", headers=auth_headers)
    assert list_resp.status_code == 200
    procs = list_resp.json()
    assert any(p["procedure_id"] == proc_id for p in procs)

    # 6. Preflight procedure
    preflight_resp = await async_client.post(
        f"/api/v1/reliability/procedures/{proc_id}/preflight",
        headers=auth_headers,
        json={"arguments": {"param_1": "test"}},
    )
    assert preflight_resp.status_code == 200
    preflight = preflight_resp.json()
    assert "can_execute" in preflight

    # 7. Execute procedure in dry_run mode
    exec_resp = await async_client.post(
        "/api/v1/reliability/executions",
        headers=auth_headers,
        json={
            "procedure_id": proc_id,
            "arguments": {"param_1": "sample text"},
            "mode": "dry_run",
        },
    )
    assert exec_resp.status_code == 201
    execution = exec_resp.json()
    exec_id = execution["execution_id"]
    assert execution["status"] == "completed"

    # 8. Checkpoints for execution
    chk_resp = await async_client.get(
        f"/api/v1/reliability/executions/{exec_id}/checkpoints",
        headers=auth_headers,
    )
    assert chk_resp.status_code == 200
    checkpoints = chk_resp.json()
    assert len(checkpoints) >= 1
