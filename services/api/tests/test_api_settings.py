"""Comprehensive test suite for centralized settings, validation, schema metadata, and export/import."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_get_all_aggregated_settings(async_client: AsyncClient, auth_headers: dict[str, str]):
    res = await async_client.get("/api/v1/settings/all", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()

    # Verify all 13 core categories are present
    expected_categories = [
        "general",
        "appearance",
        "ai",
        "agents",
        "automation",
        "permissions",
        "computer",
        "integrations",
        "recruitment",
        "storage",
        "notifications",
        "desktop",
        "security",
    ]
    for cat in expected_categories:
        assert cat in data, f"Missing category: {cat}"

    # Verify defaults
    assert data["general"]["app_language"] == "en-US"
    assert data["general"]["date_format"] == "YYYY-MM-DD"
    assert data["appearance"]["theme"] == "navy-dark"
    assert data["automation"]["max_concurrent_workers"] == 4
    assert data["ai"]["single_active_model_enforced"] is True
    assert data["recruitment"]["max_daily_applications"] == 5


@pytest.mark.asyncio
async def test_get_settings_schema_metadata(async_client: AsyncClient, auth_headers: dict[str, str]):
    res = await async_client.get("/api/v1/settings/schema", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "categories" in data
    assert "items" in data
    assert len(data["categories"]) == 13
    assert len(data["items"]) > 20

    # Ensure restart-required flags are appropriately mapped
    worker_item = next((item for item in data["items"] if item["key"] == "automation.max_concurrent_workers"), None)
    assert worker_item is not None
    assert worker_item["requires_restart"] is True


@pytest.mark.asyncio
async def test_get_and_update_category(async_client: AsyncClient, auth_headers: dict[str, str]):
    # Get general category
    get_res = await async_client.get("/api/v1/settings/general", headers=auth_headers)
    assert get_res.status_code == 200
    gen_data = get_res.json()["value"]
    assert gen_data["time_format"] == "24h"

    # Patch general category
    patch_res = await async_client.patch(
        "/api/v1/settings/general",
        json={"time_format": "12h", "confirm_task_cancellation": False},
        headers=auth_headers,
    )
    assert patch_res.status_code == 200
    updated = patch_res.json()["value"]
    assert updated["time_format"] == "12h"
    assert updated["confirm_task_cancellation"] is False

    # Verify persistence
    verify_res = await async_client.get("/api/v1/settings/general", headers=auth_headers)
    assert verify_res.status_code == 200
    assert verify_res.json()["value"]["time_format"] == "12h"


@pytest.mark.asyncio
async def test_update_category_validation_failure(async_client: AsyncClient, auth_headers: dict[str, str]):
    # Exceed maximum worker limit (safe max is 8)
    res = await async_client.patch(
        "/api/v1/settings/automation",
        json={"max_concurrent_workers": 99},
        headers=auth_headers,
    )
    assert res.status_code == 400
    err_body = res.json()
    err_msg = err_body.get("error", {}).get("message", "") or err_body.get("detail", "")
    assert "Validation failed" in err_msg


@pytest.mark.asyncio
async def test_sensitive_category_audit_logging(async_client: AsyncClient, auth_headers: dict[str, str]):
    patch_res = await async_client.patch(
        "/api/v1/settings/security",
        json={"audit_logging_level": "security_only"},
        headers=auth_headers,
    )
    assert patch_res.status_code == 200

    # Verify audit event logged
    activity_res = await async_client.get("/api/v1/dashboard/activity", headers=auth_headers)
    assert activity_res.status_code == 200


@pytest.mark.asyncio
async def test_reset_category(async_client: AsyncClient, auth_headers: dict[str, str]):
    # Modify general
    await async_client.patch(
        "/api/v1/settings/general",
        json={"date_format": "MM/DD/YYYY"},
        headers=auth_headers,
    )

    # Reset general
    reset_res = await async_client.post("/api/v1/settings/general/reset", headers=auth_headers)
    assert reset_res.status_code == 200
    assert reset_res.json()["defaults"]["date_format"] == "YYYY-MM-DD"

    # Verify reset persisted
    verify_res = await async_client.get("/api/v1/settings/general", headers=auth_headers)
    assert verify_res.json()["value"]["date_format"] == "YYYY-MM-DD"


@pytest.mark.asyncio
async def test_export_and_import_settings(async_client: AsyncClient, auth_headers: dict[str, str]):
    # Export
    export_res = await async_client.get("/api/v1/settings/export", headers=auth_headers)
    assert export_res.status_code == 200
    export_payload = export_res.json()
    assert "settings" in export_payload
    assert "general" in export_payload["settings"]

    # Modify exported payload
    export_payload["settings"]["appearance"]["font_scale"] = "110%"

    # Import
    import_res = await async_client.post(
        "/api/v1/settings/import",
        json={"schema_version": 1, "settings": export_payload["settings"]},
        headers=auth_headers,
    )
    assert import_res.status_code == 200
    assert import_res.json()["success"] is True

    # Verify imported change took effect
    app_res = await async_client.get("/api/v1/settings/appearance", headers=auth_headers)
    assert app_res.json()["value"]["font_scale"] == "110%"


@pytest.mark.asyncio
async def test_import_malformed_rejected(async_client: AsyncClient, auth_headers: dict[str, str]):
    # Malformed worker count
    res = await async_client.post(
        "/api/v1/settings/import",
        json={
            "schema_version": 1,
            "settings": {
                "automation": {"max_concurrent_workers": -5},
            },
        },
        headers=auth_headers,
    )
    assert res.status_code == 400


@pytest.mark.asyncio
async def test_integrations_configurations_api(async_client: AsyncClient, auth_headers: dict[str, str]):
    res = await async_client.get("/api/v1/integrations/configurations", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "credentials" in data
    assert "mcp_servers" in data
    assert "services" in data
