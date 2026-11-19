"""Integration tests for Job Aggregation REST API Endpoints (Stage 27)."""

import pytest
from uuid import uuid4
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_api_aggregation_unauthorized():
    """Ensure aggregation endpoints require valid authentication."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        resp = await client.get("/api/v1/job-aggregation/status")
        assert resp.status_code == 401


@pytest.mark.asyncio
async def test_api_aggregation_overview_and_diagnostics(auth_headers):
    """Test overview status and diagnostics endpoints."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Status
        resp = await client.get("/api/v1/job-aggregation/status", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_canonical_jobs" in data
        assert "total_source_observations" in data
        assert "confirmed_duplicate_merges" in data

        # Diagnostics
        resp_diag = await client.get("/api/v1/job-aggregation/diagnostics", headers=auth_headers)
        assert resp_diag.status_code == 200
        diag = resp_diag.json()
        assert "status" in diag
        assert "canonical_jobs_count" in diag


@pytest.mark.asyncio
async def test_api_process_single_and_batch_observation(auth_headers):
    """Test ingesting single observations and batches via API."""
    prefix = uuid4().hex[:6]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Single Ingestion
        obs_payload = {
            "observation_id": f"obs_api_{prefix}",
            "source_id": "src_lever",
            "provider": "lever",
            "employer_name": f"API Corp {prefix}",
            "title": "Principal Systems Engineer",
            "source_url": f"https://apicorp.example/jobs/{prefix}",
            "native_posting_id": f"req_api_{prefix}",
            "description_text": "Building mission-critical systems and APIs.",
            "location_raw": "Austin, TX",
            "employment_type": "full_time",
            "workplace_type": "hybrid",
            "salary_raw": "$180,000 - $220,000",
        }
        resp = await client.post("/api/v1/job-aggregation/process", json=obs_payload, headers=auth_headers)
        assert resp.status_code == 200
        job = resp.json()
        assert job["display_title"] == "Principal Systems Engineer"
        job_id = job["id"]

        # 2. Get canonical job by ID
        resp_get = await client.get(f"/api/v1/job-aggregation/jobs/{job_id}", headers=auth_headers)
        assert resp_get.status_code == 200
        assert resp_get.json()["id"] == job_id

        # 3. Get sources
        resp_src = await client.get(f"/api/v1/job-aggregation/jobs/{job_id}/sources", headers=auth_headers)
        assert resp_src.status_code == 200
        sources = resp_src.json()
        assert len(sources) >= 1
        assert sources[0]["source_observation_id"] == f"obs_api_{prefix}"

        # 4. Get history
        resp_hist = await client.get(f"/api/v1/job-aggregation/jobs/{job_id}/history", headers=auth_headers)
        assert resp_hist.status_code == 200
        history = resp_hist.json()
        assert len(history) >= 1

        # 5. List jobs
        resp_list = await client.get("/api/v1/job-aggregation/jobs?query=Principal Systems", headers=auth_headers)
        assert resp_list.status_code == 200
        jobs = resp_list.json()
        assert any(j["id"] == job_id for j in jobs)

        # 6. Batch Ingestion (Array body)
        batch_payload = [
            {
                "id": f"obs_batch_1_{prefix}",
                "source_id": "src_gh",
                "provider": "greenhouse",
                "employer_name": f"Batch Corp {prefix}",
                "title": "Data Engineer",
                "source_url": f"https://batch.example/{prefix}/1",
                "native_posting_id": f"batch_1_{prefix}",
                "description_text": "Building ETL and analytics pipelines.",
            }
        ]
        resp_batch = await client.post("/api/v1/job-aggregation/process-batch", json=batch_payload, headers=auth_headers)
        assert resp_batch.status_code == 200
        task = resp_batch.json()
        assert task["observations_total"] == 1
        assert task["status"] == "completed"

        # 7. List Tasks
        resp_tasks = await client.get("/api/v1/job-aggregation/tasks", headers=auth_headers)
        assert resp_tasks.status_code == 200
        tasks = resp_tasks.json()
        assert len(tasks) >= 1


@pytest.mark.asyncio
async def test_api_employers_and_resolution(auth_headers):
    """Test employer endpoints, listing, and on-demand resolution."""
    prefix = uuid4().hex[:6]
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Resolve employer using query parameters
        params = {
            "raw_name": f"Acme Dynamic {prefix}",
            "source_url": f"https://acme-{prefix}.example/careers",
            "provider": "greenhouse",
        }
        resp = await client.post("/api/v1/job-aggregation/employers/resolve", params=params, headers=auth_headers)
        assert resp.status_code == 200
        emp = resp.json()
        assert emp["name"] == f"Acme Dynamic {prefix}"
        emp_id = emp["id"]

        # List employers
        resp_list = await client.get("/api/v1/job-aggregation/employers", headers=auth_headers)
        assert resp_list.status_code == 200
        employers = resp_list.json()
        assert any(e["id"] == emp_id for e in employers)

        # Get employer by ID
        resp_get = await client.get(f"/api/v1/job-aggregation/employers/{emp_id}", headers=auth_headers)
        assert resp_get.status_code == 200
        assert resp_get.json()["id"] == emp_id

        # Get employer evidence
        resp_ev = await client.get(f"/api/v1/job-aggregation/employers/{emp_id}/evidence", headers=auth_headers)
        assert resp_ev.status_code == 200


@pytest.mark.asyncio
async def test_api_duplicates_and_settings(auth_headers):
    """Test duplicate review endpoints and settings management."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # List duplicates
        resp_dups = await client.get("/api/v1/job-aggregation/duplicates", headers=auth_headers)
        assert resp_dups.status_code == 200
        assert isinstance(resp_dups.json(), list)

        # Conflicts
        resp_conf = await client.get("/api/v1/job-aggregation/conflicts", headers=auth_headers)
        assert resp_conf.status_code == 200
        assert isinstance(resp_conf.json(), list)

        # Settings GET
        resp_sett = await client.get("/api/v1/job-aggregation/settings", headers=auth_headers)
        assert resp_sett.status_code == 200
        settings_data = resp_sett.json()
        assert "min_similarity_for_auto_merge" in settings_data

        # Settings PUT
        settings_data["min_similarity_for_auto_merge"] = 0.95
        resp_put = await client.put("/api/v1/job-aggregation/settings", json=settings_data, headers=auth_headers)
        assert resp_put.status_code == 200
        assert resp_put.json()["min_similarity_for_auto_merge"] == 0.95
