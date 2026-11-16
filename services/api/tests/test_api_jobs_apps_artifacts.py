"""Integration tests for Jobs, Applications, and Artifacts REST endpoints."""

import pytest
from httpx import AsyncClient

from app.db.engine import get_db_session
from app.repositories import (
    ApplicationRepository,
    ArtifactRepository,
    JobRepository,
    ProfileRepository,
)


@pytest.mark.asyncio
async def test_jobs_unauthenticated(async_client: AsyncClient):
    response = await async_client.get("/api/v1/jobs")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_jobs_authenticated_empty(async_client: AsyncClient, auth_headers: dict[str, str]):
    response = await async_client.get("/api/v1/jobs", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert data["limit"] == 50
    assert data["offset"] == 0


@pytest.mark.asyncio
async def test_jobs_with_records(async_client: AsyncClient, auth_headers: dict[str, str]):
    async with get_db_session() as session:
        repo = JobRepository(session)
        source = await repo.get_or_create_source(
            platform_name="linkedin",
            source_url="https://linkedin.com/jobs/autonom_test_feed",
        )
        job = await repo.create_listing(
            source_id=source.id,
            external_id="ext-test-101",
            company="Acme Robotics",
            title="Principal AI Systems Architect",
            application_url="https://acme.example.com/apply/101",
            location="Remote, USA",
            work_arrangement="remote",
            salary_range="$220k - $275k",
            description="Lead autonomous agent architectures.",
        )
        job_id = job.id

    # List jobs
    response = await async_client.get("/api/v1/jobs", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    matched = [j for j in data["items"] if j["id"] == job_id]
    assert len(matched) == 1
    assert matched[0]["company"] == "Acme Robotics"
    assert matched[0]["title"] == "Principal AI Systems Architect"

    # Get single job
    single_res = await async_client.get(f"/api/v1/jobs/{job_id}", headers=auth_headers)
    assert single_res.status_code == 200
    single_data = single_res.json()
    assert single_data["id"] == job_id
    assert single_data["company"] == "Acme Robotics"


@pytest.mark.asyncio
async def test_jobs_not_found(async_client: AsyncClient, auth_headers: dict[str, str]):
    response = await async_client.get("/api/v1/jobs/nonexistent-job-id", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_applications_unauthenticated(async_client: AsyncClient):
    response = await async_client.get("/api/v1/applications")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_applications_with_records(async_client: AsyncClient, auth_headers: dict[str, str]):
    async with get_db_session() as session:
        job_repo = JobRepository(session)
        profile_repo = ProfileRepository(session)
        app_repo = ApplicationRepository(session)

        source = await job_repo.get_or_create_source("greenhouse", "https://boards.greenhouse.io/autonom")
        job = await job_repo.create_listing(
            source_id=source.id,
            external_id="gh-777",
            company="Neural Dynamics",
            title="Staff Desktop Engineer",
            application_url="https://boards.greenhouse.io/autonom/777",
        )
        profile = await profile_repo.create_profile(
            profile_name="Primary Candidate Profile",
            summary="Experienced systems engineer",
        )

        app = await app_repo.create_application(
            job_id=job.id,
            profile_id=profile.id,
            notes="Stage 09 verification test application",
        )
        app_id = app.id

        await app_repo.record_attempt(
            application_id=app.id,
            execution_status="pending",
            idempotency_key=f"attempt-{app.id}-1",
        )

    # List applications
    response = await async_client.get("/api/v1/applications", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    matched = [a for a in data["items"] if a["id"] == app_id]
    assert len(matched) == 1
    assert matched[0]["company"] == "Neural Dynamics"
    assert matched[0]["job_title"] == "Staff Desktop Engineer"
    assert len(matched[0]["attempts"]) == 1

    # Get single application
    single_res = await async_client.get(f"/api/v1/applications/{app_id}", headers=auth_headers)
    assert single_res.status_code == 200
    assert single_res.json()["id"] == app_id


@pytest.mark.asyncio
async def test_applications_not_found(async_client: AsyncClient, auth_headers: dict[str, str]):
    response = await async_client.get("/api/v1/applications/missing-app-id", headers=auth_headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_artifacts_unauthenticated(async_client: AsyncClient):
    response = await async_client.get("/api/v1/artifacts")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_artifacts_with_records(async_client: AsyncClient, auth_headers: dict[str, str]):
    async with get_db_session() as session:
        art_repo = ArtifactRepository(session)
        art = await art_repo.create_artifact(
            artifact_type="resume_pdf",
            storage_path="vault/resumes/staff_desktop_v1.pdf",
            file_size=245800,
            checksum="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",
            retention_class="permanent",
        )
        art_id = art.id

    # List artifacts
    response = await async_client.get("/api/v1/artifacts", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    matched = [a for a in data["items"] if a["id"] == art_id]
    assert len(matched) == 1
    assert matched[0]["artifact_type"] == "resume_pdf"
    assert matched[0]["file_size"] == 245800

    # Get single artifact
    single_res = await async_client.get(f"/api/v1/artifacts/{art_id}", headers=auth_headers)
    assert single_res.status_code == 200
    assert single_res.json()["id"] == art_id


@pytest.mark.asyncio
async def test_artifacts_not_found(async_client: AsyncClient, auth_headers: dict[str, str]):
    response = await async_client.get("/api/v1/artifacts/missing-art-id", headers=auth_headers)
    assert response.status_code == 404
