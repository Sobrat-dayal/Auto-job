"""REST API integration test suite for Stage 30 Recruitment Monitoring endpoints."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.core.config import settings
from app.main import app


@pytest.fixture
def auth_headers() -> dict[str, str]:
    return {"Authorization": f"Bearer {settings.api_key}"}


@pytest.mark.asyncio
async def test_monitoring_api_auth_required():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Request without auth header should fail with 401
        res = await client.get("/api/v1/recruitment-monitoring/status")
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_monitoring_status_endpoint(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.get("/api/v1/recruitment-monitoring/status", headers=auth_headers)
        assert res.status_code == 200
        data = res.json()
        assert "active_watches_count" in data
        assert "monitoring_enabled" in data
        assert "total_opportunities_count" in data


@pytest.mark.asyncio
async def test_job_watch_crud_and_preview(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Create Profile
        prof_res = await client.post(
            "/api/v1/recruitment-monitoring/profiles",
            json={"name": "Test Monitoring Profile"},
            headers=auth_headers,
        )
        assert prof_res.status_code == 201
        profile_id = prof_res.json()["id"]

        # 1. Create Watch
        payload = {
            "name": "Integration Test Watch",
            "profile_id": profile_id,
            "watch_type": "career_strategy",
            "career_strategy_id": "strat_test_001",
            "approved_sources": ["greenhouse_public"],
            "schedule_config": {
                "recurrence_type": "interval",
                "interval_minutes": 60,
                "timezone": "UTC",
                "quiet_hours": {
                    "enabled": True,
                    "start_time": "22:00",
                    "end_time": "08:00",
                    "mute_notifications": True,
                    "pause_source_monitoring": False,
                },
                "missed_run_policy": "run_latest_due",
            },
            "role_filters": {
                "roles": ["Software Engineer", "Backend Developer"],
            },
            "location_filters": {
                "locations": ["Remote", "New York, NY"],
            },
        }
        res_create = await client.post(
            "/api/v1/recruitment-monitoring/watches",
            json=payload,
            headers=auth_headers,
        )
        assert res_create.status_code == 201
        watch = res_create.json()
        watch_id = watch["id"]
        assert watch["name"] == "Integration Test Watch"
        assert watch["status"] == "active"

        # 2. Get Watch
        res_get = await client.get(
            f"/api/v1/recruitment-monitoring/watches/{watch_id}",
            headers=auth_headers,
        )
        assert res_get.status_code == 200
        assert res_get.json()["id"] == watch_id

        # 3. Schedule Preview
        res_prev = await client.get(
            f"/api/v1/recruitment-monitoring/watches/{watch_id}/schedule-preview",
            headers=auth_headers,
        )
        assert res_prev.status_code == 200
        preview = res_prev.json()
        assert len(preview["next_occurrences"]) == 5

        # 4. Pause Watch
        res_pause = await client.post(
            f"/api/v1/recruitment-monitoring/watches/{watch_id}/pause",
            headers=auth_headers,
        )
        assert res_pause.status_code == 200
        assert res_pause.json()["status"] == "paused"

        # 5. Resume Watch
        res_resume = await client.post(
            f"/api/v1/recruitment-monitoring/watches/{watch_id}/resume",
            headers=auth_headers,
        )
        assert res_resume.status_code == 200
        assert res_resume.json()["status"] == "active"

        # 6. Delete Watch
        res_del = await client.delete(
            f"/api/v1/recruitment-monitoring/watches/{watch_id}",
            headers=auth_headers,
        )
        assert res_del.status_code == 204


@pytest.mark.asyncio
async def test_monitoring_runs_and_opportunities_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Runs
        res_runs = await client.get("/api/v1/recruitment-monitoring/runs", headers=auth_headers)
        assert res_runs.status_code == 200
        assert isinstance(res_runs.json(), list)

        # Opportunities
        res_opps = await client.get("/api/v1/recruitment-monitoring/opportunities", headers=auth_headers)
        assert res_opps.status_code == 200
        assert isinstance(res_opps.json(), list)

        # Changes
        res_changes = await client.get("/api/v1/recruitment-monitoring/job-changes", headers=auth_headers)
        assert res_changes.status_code == 200
        assert isinstance(res_changes.json(), list)


@pytest.mark.asyncio
async def test_monitoring_alerts_and_diagnostics(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Alerts
        res_alerts = await client.get("/api/v1/recruitment-monitoring/alerts", headers=auth_headers)
        assert res_alerts.status_code == 200
        assert isinstance(res_alerts.json(), list)

        # Diagnostics
        res_diag = await client.get("/api/v1/recruitment-monitoring/diagnostics", headers=auth_headers)
        assert res_diag.status_code == 200
        diag_data = res_diag.json()
        assert "database_status" in diag_data
        assert "active_worker_leases" in diag_data
        assert "components_health" in diag_data


@pytest.mark.asyncio
async def test_monitoring_settings_endpoints(auth_headers):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Get settings
        res_get = await client.get("/api/v1/recruitment-monitoring/settings", headers=auth_headers)
        assert res_get.status_code == 200
        settings_data = res_get.json()
        assert "background_monitoring_enabled" in settings_data

        # Update settings
        res_patch = await client.patch(
            "/api/v1/recruitment-monitoring/settings",
            json={"default_interval_minutes": 45, "daily_request_budget": 600},
            headers=auth_headers,
        )
        assert res_patch.status_code == 200
        updated = res_patch.json()
        assert updated["default_interval_minutes"] == 45
        assert updated["daily_request_budget"] == 600
