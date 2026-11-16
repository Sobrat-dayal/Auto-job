"""Integration tests for Stage 04 Storage, Settings, Profiles, and Credentials API endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_storage_endpoints(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Storage Status
    res = await async_client.get("/api/v1/storage/status", headers=auth_headers)
    assert res.status_code == 200
    status_data = res.json()
    assert "database_exists" in status_data
    assert "database_size_bytes" in status_data
    assert "total_backups_count" in status_data

    # 2. Storage Health & Integrity
    health_res = await async_client.get("/api/v1/storage/health", headers=auth_headers)
    assert health_res.status_code == 200
    health_data = health_res.json()
    assert health_data["integrity_check_passed"] is True
    assert health_data["foreign_keys_passed"] is True

    # 3. Create Online Backup
    backup_res = await async_client.post("/api/v1/storage/backups", headers=auth_headers)
    assert backup_res.status_code == 201
    manifest = backup_res.json()
    assert manifest["integrity_check_passed"] is True
    assert "backup_id" in manifest

    # 4. List Backups
    list_res = await async_client.get("/api/v1/storage/backups", headers=auth_headers)
    assert list_res.status_code == 200
    backups = list_res.json()
    assert len(backups) >= 1
    assert any(b["backup_id"] == manifest["backup_id"] for b in backups)


@pytest.mark.asyncio
async def test_settings_api(async_client: AsyncClient, auth_headers: dict[str, str]):
    # Set setting
    patch_res = await async_client.patch(
        "/api/v1/settings/editor",
        json={"value": {"font_size": 14, "minimap": False}, "scope": "user"},
        headers=auth_headers,
    )
    assert patch_res.status_code == 200

    # Get setting
    get_res = await async_client.get("/api/v1/settings/editor", headers=auth_headers)
    assert get_res.status_code == 200
    assert get_res.json()["value"]["font_size"] == 14

    # List settings
    list_res = await async_client.get("/api/v1/settings", headers=auth_headers)
    assert list_res.status_code == 200
    assert any(s["key"] == "editor" for s in list_res.json())


@pytest.mark.asyncio
async def test_profile_and_credentials_api(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Create Profile
    prof_res = await async_client.post(
        "/api/v1/profiles",
        json={
            "profile_name": "Full Stack Architect",
            "summary": "Specialist in autonomous desktop agents",
            "contact_info": {"email": "architect@autonom.local", "location": "Remote"},
        },
        headers=auth_headers,
    )
    assert prof_res.status_code == 201
    pid = prof_res.json()["id"]

    # 2. Get Profile with Decrypted Contact
    get_prof = await async_client.get(f"/api/v1/profiles/{pid}", headers=auth_headers)
    assert get_prof.status_code == 200
    prof_data = get_prof.json()
    assert prof_data["profile_name"] == "Full Stack Architect"
    assert prof_data["contact_info"]["email"] == "architect@autonom.local"

    # 3. Store Credential
    cred_res = await async_client.post(
        "/api/v1/integrations/credentials",
        json={
            "provider": "openai",
            "credential_type": "api_key",
            "secret_value": "sk-proj-testsecret1234567890",
        },
        headers=auth_headers,
    )
    assert cred_res.status_code == 201

    # 4. List Credential Status (Must NOT expose secret value)
    status_res = await async_client.get("/api/v1/integrations/credentials/status", headers=auth_headers)
    assert status_res.status_code == 200
    creds = status_res.json()
    assert any(c["provider"] == "openai" for c in creds)
    for c in creds:
        assert "secret" not in c
        assert "secret_value" not in c
        assert "encrypted_blob" not in c
