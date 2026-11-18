"""Integration tests for Stage 22 GitHub & Technical Portfolio FastAPI REST API endpoints."""

from unittest.mock import AsyncMock, patch
import pytest
from httpx import AsyncClient

from app.recruitment.github.contracts import (
    CandidateProject,
    CandidateSkill,
    CandidateStatus,
    ConnectionMode,
    ConnectionStatus,
    GitHubConnection,
    RepoVisibility,
    RepositoryMetadata,
    SyncJobRecord,
    SyncStatus,
    TechCategory,
    TechnologyFinding,
)
from app.recruitment.github.service import get_github_service


@pytest.mark.asyncio
async def test_github_status_and_diagnostics(async_client: AsyncClient, auth_headers: dict[str, str]):
    # Status endpoint
    res = await async_client.get("/api/v1/github/status", headers=auth_headers)
    assert res.status_code == 200
    data = res.json()
    assert "rate_limit" in data
    assert "review_queue" in data

    # Diagnostics endpoint
    res_diag = await async_client.get("/api/v1/github/diagnostics", headers=auth_headers)
    assert res_diag.status_code == 200
    diag = res_diag.json()
    assert "rate_limit_remaining" in diag
    assert "total_discovered_repositories" in diag


@pytest.mark.asyncio
async def test_github_connection_lifecycle(async_client: AsyncClient, auth_headers: dict[str, str]):
    svc = get_github_service()

    # Mock live GitHub /user check
    with patch("app.recruitment.github.client.rest.GitHubRestClient.get", new_callable=AsyncMock) as mock_get:
        mock_get.return_value = {
            "id": 12345,
            "login": "test_developer",
            "name": "Test Developer",
            "public_repos": 15,
            "followers": 100,
            "following": 10,
        }

        # 1. Connect Account
        payload = {
            "username": "test_developer",
            "mode": "public_only",
            "profile_id": "prof_primary_applicant",
        }
        res = await async_client.post("/api/v1/github/connections", json=payload, headers=auth_headers)
        assert res.status_code == 201
        conn = res.json()
        assert conn["login"] == "test_developer"
        conn_id = conn["id"]

        # 2. Get connection
        res_get = await async_client.get(f"/api/v1/github/connections/{conn_id}", headers=auth_headers)
        assert res_get.status_code == 200
        assert res_get.json()["id"] == conn_id

        # 3. Permissions
        res_perm = await async_client.get(f"/api/v1/github/connections/{conn_id}/permissions", headers=auth_headers)
        assert res_perm.status_code == 200
        assert res_perm.json()["login"] == "test_developer"

        # 4. List connections
        res_list = await async_client.get("/api/v1/github/connections", headers=auth_headers)
        assert res_list.status_code == 200
        assert any(c["id"] == conn_id for c in res_list.json())

        # 5. Disconnect
        res_dc = await async_client.post(f"/api/v1/github/connections/{conn_id}/disconnect", headers=auth_headers)
        assert res_dc.status_code == 200
        assert res_dc.json()["disconnected"] is True


@pytest.mark.asyncio
async def test_manual_repository_ingest_and_selection(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. Ingest public repository URL
    payload = {
        "url": "https://github.com/torvalds/linux",
    }
    res = await async_client.post("/api/v1/github/repositories/manual", json=payload, headers=auth_headers)
    assert res.status_code == 201
    repo = res.json()
    assert repo["name"] == "linux"
    assert repo["owner"] == "torvalds"
    repo_id = repo["id"]

    # 2. List repositories
    res_list = await async_client.get("/api/v1/github/repositories", headers=auth_headers)
    assert res_list.status_code == 200
    assert any(r["id"] == repo_id for r in res_list.json())

    # 3. Select repository for analysis
    select_payload = {"allow_source_inspection": True}
    res_sel = await async_client.post(f"/api/v1/github/repositories/{repo_id}/select", json=select_payload, headers=auth_headers)
    assert res_sel.status_code == 200
    assert res_sel.json()["is_selected"] is True

    # 4. Deselect repository
    res_desel = await async_client.post(f"/api/v1/github/repositories/{repo_id}/deselect", headers=auth_headers)
    assert res_desel.status_code == 200
    assert res_desel.json()["is_selected"] is False


@pytest.mark.asyncio
async def test_candidate_skills_and_projects_review(async_client: AsyncClient, auth_headers: dict[str, str]):
    svc = get_github_service()

    # Pre-register candidate skill
    candidate_skill = CandidateSkill(
        id="csk_api_test",
        name="PyTorch",
        category=TechCategory.AI_ML,
        version="2.4.0",
        proficiency_hint="advanced",
        evidence_repo_id="repo_test_ml",
        evidence_repo_name="ml-pipeline",
    )
    svc.review_mgr.register_skills([candidate_skill])

    # 1. List candidate skills
    res = await async_client.get("/api/v1/github/skill-candidates", headers=auth_headers)
    assert res.status_code == 200
    skills = res.json()
    assert any(s["id"] == "csk_api_test" for s in skills)

    # 2. Confirm candidate skill (promotes into Stage 21 profile)
    confirm_payload = {
        "profile_id": "prof_primary_applicant",
        "modified_data": {"proficiency": "expert"},
    }
    res_conf = await async_client.post("/api/v1/github/skill-candidates/csk_api_test/confirm", json=confirm_payload, headers=auth_headers)
    assert res_conf.status_code == 200
    confirmed = res_conf.json()
    assert confirmed["status"] == "confirmed"

    # Pre-register candidate project
    candidate_project = CandidateProject(
        id="cpj_api_test",
        title="ML Pipeline Engine",
        description="Scalable deep learning inference backend",
        repo_id="repo_test_ml",
        repo_name="ml-pipeline",
        repo_url="https://github.com/test/ml-pipeline",
        technologies=["PyTorch", "FastAPI"],
    )
    svc.review_mgr.register_project(candidate_project)

    # 3. Reject candidate project
    res_rej = await async_client.post("/api/v1/github/candidates/cpj_api_test/reject", headers=auth_headers)
    assert res_rej.status_code == 200
    assert res_rej.json()["status"] == "rejected"
