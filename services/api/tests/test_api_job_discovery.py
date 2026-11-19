"""Integration tests for Job Discovery REST API Endpoints (Stage 26)."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_api_discovery_overview(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/recruitment/discovery/overview", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_sources" in data
        assert "enabled_sources" in data
        assert "active_postings_count" in data


@pytest.mark.asyncio
async def test_api_list_connectors(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/recruitment/discovery/connectors", headers=auth_headers)
        assert resp.status_code == 200
        connectors = resp.json()
        assert len(connectors) >= 6
        ids = [c["connector_id"] for c in connectors]
        assert "greenhouse" in ids
        assert "lever" in ids
        assert "ashby" in ids
        assert "usajobs" in ids


@pytest.mark.asyncio
async def test_api_sources_crud(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Create source
        payload = {
            "name": "Datadog Careers",
            "connector_id": "greenhouse",
            "official_domain": "boards-api.greenhouse.io",
            "board_token": "datadog",
            "employer_name": "Datadog",
            "is_enabled": True,
            "rate_limit_rpm": 25,
        }
        res = await client.post("/api/v1/recruitment/discovery/sources", json=payload, headers=auth_headers)
        assert res.status_code == 201
        source_id = res.json()["id"]

        # 2. Get source
        get_res = await client.get(f"/api/v1/recruitment/discovery/sources/{source_id}", headers=auth_headers)
        assert get_res.status_code == 200
        assert get_res.json()["name"] == "Datadog Careers"

        # 3. Update source
        patch_res = await client.patch(
            f"/api/v1/recruitment/discovery/sources/{source_id}",
            json={"rate_limit_rpm": 40},
            headers=auth_headers,
        )
        assert patch_res.status_code == 200
        assert patch_res.json()["rate_limit_rpm"] == 40

        # 4. Delete source
        del_res = await client.delete(f"/api/v1/recruitment/discovery/sources/{source_id}", headers=auth_headers)
        assert del_res.status_code == 200
        assert del_res.json()["deleted"] is True


@pytest.mark.asyncio
async def test_api_manual_import(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        payload = {
            "title": "Senior Distributed Systems Engineer",
            "employer_name": "Acme Corp",
            "description": "Design distributed consensus protocols in Rust.",
            "location": "Remote",
            "work_arrangement": "remote",
            "compensation_text": "$180,000 - $220,000 USD",
        }
        res = await client.post("/api/v1/recruitment/discovery/import/manual", json=payload, headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert data["title"] == "Senior Distributed Systems Engineer"
        assert data["employer"] == "Acme Corp"
        assert data["availability"] == "available"


@pytest.mark.asyncio
async def test_api_tasks_and_settings(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create task
        task_payload = {"source_ids": ["src_greenhouse_stripe"], "max_postings": 50}
        task_res = await client.post("/api/v1/recruitment/discovery/tasks", json=task_payload, headers=auth_headers)
        assert task_res.status_code == 202
        task_id = task_res.json()["id"]

        # Get settings
        set_res = await client.get("/api/v1/recruitment/discovery/settings", headers=auth_headers)
        assert set_res.status_code == 200
        assert "max_concurrent_sources" in set_res.json()
