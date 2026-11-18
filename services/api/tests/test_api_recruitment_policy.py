"""Integration tests for Recruitment Policy REST API Endpoints (Stage 25)."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app



@pytest.mark.asyncio
async def test_api_list_and_get_strategies(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/recruitment/career-strategies", headers=auth_headers)
        assert resp.status_code == 200
        strategies = resp.json()
        assert len(strategies) >= 1
        assert any(s["title"] == "Backend & Distributed Systems Focus" for s in strategies)

        # Get first strategy
        first_id = strategies[0]["id"]
        detail_resp = await client.get(f"/api/v1/recruitment/career-strategies/{first_id}", headers=auth_headers)
        assert detail_resp.status_code == 200
        assert detail_resp.json()["id"] == first_id


@pytest.mark.asyncio
async def test_api_create_and_activate_strategy(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create
        create_payload = {
            "title": "API Test Strategy",
            "description": "Created via automated test",
            "is_active": False,
            "target_roles": [
                {"title": "DevOps Engineer", "role_family": "cloud_devops", "seniority": "mid_level"}
            ],
        }
        res = await client.post("/api/v1/recruitment/career-strategies", json=create_payload, headers=auth_headers)
        assert res.status_code == 201
        strat_id = res.json()["id"]

        # Activate
        act_res = await client.post(f"/api/v1/recruitment/career-strategies/{strat_id}/activate", headers=auth_headers)
        assert act_res.status_code == 200
        assert act_res.json()["is_active"] is True


@pytest.mark.asyncio
async def test_api_simulate_policy(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        sim_payload = {
            "synthetic_job": {
                "title": "Backend Systems Engineer",
                "employer_name": "TechGlobal",
                "work_arrangement": "remote",
                "compensation_min": 130000.0,
            }
        }
        resp = await client.post("/api/v1/recruitment/policies/simulate", json=sim_payload, headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "decision" in data
        assert data["decision"]["job_title"] == "Backend Systems Engineer"
        assert "eligibility_assessment" in data["decision"]


@pytest.mark.asyncio
async def test_api_budgets_and_autonomy_status(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Autonomy status
        auto_res = await client.get("/api/v1/recruitment/autonomy/status", headers=auth_headers)
        assert auto_res.status_code == 200
        auto_data = auto_res.json()
        assert "active_autonomy_mode" in auto_data
        assert "capabilities" in auto_data

        # Budgets
        bud_res = await client.get("/api/v1/recruitment/budgets", headers=auth_headers)
        assert bud_res.status_code == 200
        bud_data = bud_res.json()
        assert bud_data["max_daily_applications"] > 0

        # Diagnostics
        diag_res = await client.get("/api/v1/recruitment/policy-diagnostics", headers=auth_headers)
        assert diag_res.status_code == 200
        assert diag_res.json()["status"] == "healthy"
