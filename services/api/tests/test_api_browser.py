"""Integration tests for the /api/v1/browser REST endpoints."""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_browser_endpoints_unauthenticated(async_client: AsyncClient):
    resp = await async_client.get("/api/v1/browser/status")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_browser_status_authenticated(async_client: AsyncClient, auth_headers: dict[str, str]):
    resp = await async_client.get("/api/v1/browser/status", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["playwright_available"] is True
    assert "chromium" in data["installed_browsers"]
    assert data["default_headless"] is True


@pytest.mark.asyncio
async def test_browser_profiles_crud(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Create profile
    payload = {
        "name": "Job Application Test Profile",
        "description": "Profile for automated ATS testing",
        "domain_scopes": ["greenhouse.io", "lever.co"],
    }
    create_resp = await async_client.post("/api/v1/browser/profiles", json=payload, headers=auth_headers)
    assert create_resp.status_code == 201
    profile = create_resp.json()
    assert profile["name"] == "Job Application Test Profile"
    assert "greenhouse.io" in profile["domain_scopes"]

    # 2. List profiles
    list_resp = await async_client.get("/api/v1/browser/profiles", headers=auth_headers)
    assert list_resp.status_code == 200
    profiles = list_resp.json()
    assert len(profiles) >= 1
    assert any(p["id"] == profile["id"] for p in profiles)


@pytest.mark.asyncio
async def test_browser_tasks_crud(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Create task
    task_payload = {
        "goal": "Navigate to job board and find senior backend listings",
        "max_steps": 10,
    }
    create_resp = await async_client.post("/api/v1/browser/tasks", json=task_payload, headers=auth_headers)
    assert create_resp.status_code == 201
    task = create_resp.json()
    assert task["goal"] == task_payload["goal"]
    assert task["status"] == "pending"

    # 2. List tasks
    list_resp = await async_client.get("/api/v1/browser/tasks", headers=auth_headers)
    assert list_resp.status_code == 200
    tasks = list_resp.json()
    assert len(tasks) >= 1


@pytest.mark.asyncio
async def test_browser_downloads_list(async_client: AsyncClient, auth_headers: dict[str, str]):
    resp = await async_client.get("/api/v1/browser/downloads", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


@pytest.mark.asyncio
async def test_browser_sessions_list(async_client: AsyncClient, auth_headers: dict[str, str]):
    resp = await async_client.get("/api/v1/browser/sessions", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
