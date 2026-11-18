"""GitHub & Technical Portfolio Intelligence REST API endpoints for Stage 22."""

from __future__ import annotations

import logging
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field

from app.api.dependencies import AuthDep
from app.recruitment.github.contracts import (
    CandidateProject,
    CandidateSkill,
    CommitEvidence,
    ConnectionMode,
    ContributionFinding,
    FileContentSnippet,
    GitHubConnection,
    GitHubDiagnostics,
    PullRequestEvidence,
    RepositoryArchitecture,
    RepositoryMetadata,
    SourceTreeEntry,
    SyncJobRecord,
    TechnologyFinding,
)
from app.recruitment.github.errors import (
    CandidateNotFoundError,
    GitHubAuthenticationError,
    GitHubConnectionNotFoundError,
    GitHubIntelligenceError,
    GitHubPermissionDeniedError,
    GitHubRateLimitExceededError,
    GitHubRepositoryNotFoundError,
    GitHubSourceAnalysisError,
    InvalidRepositoryURLError,
)
from app.recruitment.github.service import (
    GitHubIntelligenceService,
    get_github_service,
)

logger = logging.getLogger("autonom.api.github")

router = APIRouter(prefix="/github", tags=["github"])


def _map_exception(exc: Exception) -> HTTPException:
    if isinstance(exc, GitHubConnectionNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, GitHubRepositoryNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, CandidateNotFoundError):
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))
    if isinstance(exc, GitHubAuthenticationError):
        return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(exc))
    if isinstance(exc, GitHubPermissionDeniedError):
        return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc))
    if isinstance(exc, GitHubRateLimitExceededError):
        headers = {}
        if exc.reset_timestamp:
            headers["X-RateLimit-Reset"] = str(exc.reset_timestamp)
        return HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=str(exc),
            headers=headers,
        )
    if isinstance(exc, InvalidRepositoryURLError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    if isinstance(exc, GitHubSourceAnalysisError):
        return HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc))
    if isinstance(exc, GitHubIntelligenceError):
        return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))
    return HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(exc))


# =============================================================================
# Request Schemas
# =============================================================================

class ConnectGitHubRequest(BaseModel):
    username: str = Field(..., description="GitHub username or organization handle")
    mode: ConnectionMode = Field(
        default=ConnectionMode.PUBLIC_ONLY,
        description="Connection mode: public_only, personal_access_token, or manual_url",
    )
    access_token: Optional[str] = Field(
        default=None,
        description="Fine-grained or classic GitHub Personal Access Token",
    )
    profile_id: str = Field(
        default="prof_primary_applicant",
        description="Target applicant profile ID for portfolio sync",
    )


class ManualRepoRequest(BaseModel):
    url: str = Field(..., description="Full GitHub repository URL (e.g. https://github.com/owner/repo)")
    connection_id: Optional[str] = Field(default=None, description="Optional associated connection ID")


class DiscoverReposRequest(BaseModel):
    connection_id: str = Field(..., description="GitHub Connection ID to run discovery for")


class SelectRepoRequest(BaseModel):
    allow_source_inspection: bool = Field(
        default=True,
        description="Whether to permit AST/manifest and source code inspection",
    )


class ConfirmCandidateRequest(BaseModel):
    profile_id: str = Field(default="prof_primary_applicant", description="Target profile ID")
    modified_data: Optional[dict[str, Any]] = Field(
        default=None,
        description="Optional applicant corrections or adjustments before promoting to profile",
    )


# =============================================================================
# Diagnostics & High-Level Status
# =============================================================================

@router.get("/status", summary="Get GitHub portfolio integration status")
async def get_github_status(
    auth: AuthDep,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> dict[str, Any]:
    """Returns summarized system status for GitHub portfolio intelligence."""
    diag = svc.get_diagnostics()
    return {
        "status": "ready" if diag.total_connections > 0 else "not_configured",
        "total_connections": diag.total_connections,
        "active_user": diag.active_connection_user,
        "total_discovered_repositories": diag.total_discovered_repositories,
        "total_selected_repositories": diag.total_selected_repositories,
        "total_analyzed_repositories": diag.total_analyzed_repositories,
        "rate_limit": {
            "remaining": diag.rate_limit_remaining,
            "limit": diag.rate_limit_limit,
        },
        "review_queue": {
            "pending_skills": diag.pending_skill_candidates,
            "pending_projects": diag.pending_project_candidates,
            "confirmed_claims": diag.confirmed_claims_count,
        },
        "cache_entries": diag.cached_etag_entries,
        "errors": diag.sync_error_count,
    }


@router.get("/diagnostics", response_model=GitHubDiagnostics, summary="Detailed subsystem diagnostics")
async def get_diagnostics(
    auth: AuthDep,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> GitHubDiagnostics:
    return svc.get_diagnostics()


# =============================================================================
# Account Connection Management
# =============================================================================

@router.get("/connections", response_model=list[GitHubConnection], summary="List connected GitHub accounts")
async def list_connections(
    auth: AuthDep,
    profile_id: Optional[str] = Query(None, description="Filter by applicant profile ID"),
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> list[GitHubConnection]:
    return svc.list_connections(profile_id=profile_id)


@router.post("/connections", response_model=GitHubConnection, status_code=status.HTTP_201_CREATED, summary="Connect GitHub account")
async def connect_account(
    auth: AuthDep,
    req: ConnectGitHubRequest,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> GitHubConnection:
    try:
        return await svc.connect_account(
            username=req.username,
            mode=req.mode,
            access_token=req.access_token,
            profile_id=req.profile_id,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/connections/{connection_id}", response_model=GitHubConnection, summary="Get connection details")
async def get_connection(
    auth: AuthDep,
    connection_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> GitHubConnection:
    try:
        return svc.get_connection(connection_id)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/connections/{connection_id}/disconnect", summary="Disconnect and revoke GitHub connection")
async def disconnect_account(
    auth: AuthDep,
    connection_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> dict[str, Any]:
    try:
        res = svc.disconnect(connection_id)
        return {"connection_id": connection_id, "disconnected": res}
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/connections/{connection_id}/permissions", summary="Get connection scope and permission report")
async def get_connection_permissions(
    auth: AuthDep,
    connection_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> dict[str, Any]:
    try:
        conn = svc.get_connection(connection_id)
        return {
            "connection_id": conn.id,
            "login": conn.login,
            "mode": conn.mode,
            "status": conn.status,
            "scopes": conn.scopes,
            "can_access_private": conn.can_access_private,
            "connected_at": conn.connected_at,
            "last_validated_at": conn.last_validated_at,
        }
    except Exception as exc:
        raise _map_exception(exc) from exc


# =============================================================================
# Repository Discovery & Ingestion
# =============================================================================

@router.get("/repositories", response_model=list[RepositoryMetadata], summary="List discovered or added repositories")
async def list_repositories(
    auth: AuthDep,
    connection_id: Optional[str] = Query(None, description="Filter by connection ID"),
    only_selected: bool = Query(False, description="Filter to only selected repositories"),
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> list[RepositoryMetadata]:
    return svc.list_repositories(connection_id=connection_id, only_selected=only_selected)


@router.post("/repositories/discover", response_model=list[RepositoryMetadata], summary="Run repository discovery on connected account")
async def discover_repositories(
    auth: AuthDep,
    req: DiscoverReposRequest,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> list[RepositoryMetadata]:
    try:
        return await svc.discover_repositories(req.connection_id)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/repositories/manual", response_model=RepositoryMetadata, status_code=status.HTTP_201_CREATED, summary="Add repository by public URL")
async def add_manual_repository(
    auth: AuthDep,
    req: ManualRepoRequest,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> RepositoryMetadata:
    try:
        return await svc.add_manual_repository(url=req.url, connection_id=req.connection_id)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/repositories/{repo_id}", response_model=RepositoryMetadata, summary="Get repository metadata")
async def get_repository(
    auth: AuthDep,
    repo_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> RepositoryMetadata:
    try:
        return svc.get_repository(repo_id)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/repositories/{repo_id}/select", response_model=RepositoryMetadata, summary="Select repository for deep analysis")
async def select_repository(
    auth: AuthDep,
    repo_id: str,
    req: SelectRepoRequest,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> RepositoryMetadata:
    try:
        return svc.select_repository(repo_id, allow_source_inspection=req.allow_source_inspection)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/repositories/{repo_id}/deselect", response_model=RepositoryMetadata, summary="Deselect repository")
async def deselect_repository(
    auth: AuthDep,
    repo_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> RepositoryMetadata:
    try:
        return svc.deselect_repository(repo_id)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/repositories/{repo_id}/sync", response_model=RepositoryMetadata, summary="Sync repository metadata from GitHub API")
async def sync_repository_metadata(
    auth: AuthDep,
    repo_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> RepositoryMetadata:
    try:
        return await svc.meta_sync.sync_metadata(repo_id)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/repositories/{repo_id}/sync-status", summary="Get sync and analysis status")
async def get_repository_sync_status(
    auth: AuthDep,
    repo_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> dict[str, Any]:
    try:
        repo = svc.get_repository(repo_id)
        return {
            "repo_id": repo.id,
            "full_name": repo.full_name,
            "sync_status": repo.sync_status,
            "last_synced_at": repo.last_synced_at,
        }
    except Exception as exc:
        raise _map_exception(exc) from exc


# =============================================================================
# Code & Architectural Intelligence
# =============================================================================

@router.get("/repositories/{repo_id}/languages", summary="Get repository language byte distribution")
async def get_repository_languages(
    auth: AuthDep,
    repo_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> dict[str, Any]:
    try:
        repo = svc.get_repository(repo_id)
        total_bytes = sum(repo.languages.values())
        percentages = {
            lang: round((count / total_bytes) * 100, 2) if total_bytes > 0 else 0.0
            for lang, count in repo.languages.items()
        }
        return {
            "repo_id": repo.id,
            "total_bytes": total_bytes,
            "raw_bytes": repo.languages,
            "percentages": percentages,
        }
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/repositories/{repo_id}/technologies", response_model=list[TechnologyFinding], summary="Get identified frameworks and tools")
async def get_repository_technologies(
    auth: AuthDep,
    repo_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> list[TechnologyFinding]:
    try:
        svc.get_repository(repo_id)  # verify existence
        return svc.get_technologies(repo_id)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/repositories/{repo_id}/architecture", response_model=Optional[RepositoryArchitecture], summary="Get architectural analysis")
async def get_repository_architecture(
    auth: AuthDep,
    repo_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> Optional[RepositoryArchitecture]:
    try:
        svc.get_repository(repo_id)
        return svc.get_architecture(repo_id)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/repositories/{repo_id}/contributions", response_model=list[ContributionFinding], summary="Get contribution findings")
async def get_repository_contributions(
    auth: AuthDep,
    repo_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> list[ContributionFinding]:
    try:
        svc.get_repository(repo_id)
        return svc.get_contributions(repo_id)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/repositories/{repo_id}/commits", response_model=list[CommitEvidence], summary="Get evaluated commit evidence")
async def get_repository_commits(
    auth: AuthDep,
    repo_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> list[CommitEvidence]:
    try:
        svc.get_repository(repo_id)
        return svc.get_commits(repo_id)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/repositories/{repo_id}/pull-requests", response_model=list[PullRequestEvidence], summary="Get evaluated pull requests")
async def get_repository_pull_requests(
    auth: AuthDep,
    repo_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> list[PullRequestEvidence]:
    try:
        svc.get_repository(repo_id)
        return svc.get_pull_requests(repo_id)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/repositories/{repo_id}/tree", response_model=list[SourceTreeEntry], summary="Inspect repository file tree")
async def get_repository_tree(
    auth: AuthDep,
    repo_id: str,
    force_refresh: bool = Query(False, description="Bypass cache and force re-inspection"),
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> list[SourceTreeEntry]:
    try:
        return await svc.tree_inspector.inspect_tree(repo_id, force_refresh=force_refresh)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.get("/repositories/{repo_id}/file", response_model=FileContentSnippet, summary="Fetch redacted file content snippet")
async def get_repository_file(
    auth: AuthDep,
    repo_id: str,
    path: str = Query(..., description="Relative path of file within repository"),
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> FileContentSnippet:
    try:
        return await svc.source_fetcher.fetch_file(repo_id, path)
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/repositories/{repo_id}/analyze", response_model=SyncJobRecord, summary="Trigger full multi-stage analysis")
async def trigger_repository_analysis(
    auth: AuthDep,
    repo_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> SyncJobRecord:
    try:
        return await svc.analyze_repository(repo_id)
    except Exception as exc:
        raise _map_exception(exc) from exc


# =============================================================================
# Analysis Jobs & Execution History
# =============================================================================

@router.get("/analysis-jobs", response_model=list[SyncJobRecord], summary="List analysis jobs")
async def list_analysis_jobs(
    auth: AuthDep,
    repo_id: Optional[str] = Query(None, description="Filter jobs by repository ID"),
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> list[SyncJobRecord]:
    return svc.list_sync_jobs(repo_id=repo_id)


@router.get("/analysis-jobs/{job_id}", response_model=SyncJobRecord, summary="Get analysis job status")
async def get_analysis_job(
    auth: AuthDep,
    job_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> SyncJobRecord:
    job = svc.get_sync_job(job_id)
    if not job:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Job '{job_id}' not found.")
    return job


# =============================================================================
# Candidate Review & Profile Synchronization
# =============================================================================

@router.get("/skill-candidates", response_model=list[CandidateSkill], summary="List skill candidates awaiting review")
async def list_skill_candidates(
    auth: AuthDep,
    repo_id: Optional[str] = Query(None, description="Filter candidates by repository ID"),
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> list[CandidateSkill]:
    return svc.list_skill_candidates(repo_id=repo_id)


@router.get("/project-candidates", response_model=list[CandidateProject], summary="List project candidates awaiting review")
async def list_project_candidates(
    auth: AuthDep,
    repo_id: Optional[str] = Query(None, description="Filter candidates by repository ID"),
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> list[CandidateProject]:
    return svc.list_project_candidates(repo_id=repo_id)


@router.post("/skill-candidates/{candidate_id}/confirm", response_model=CandidateSkill, summary="Confirm and promote skill candidate to profile")
async def confirm_skill_candidate(
    auth: AuthDep,
    candidate_id: str,
    req: ConfirmCandidateRequest,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> CandidateSkill:
    try:
        return svc.confirm_skill_candidate(
            candidate_id=candidate_id,
            profile_id=req.profile_id,
            modified_data=req.modified_data,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/project-candidates/{candidate_id}/confirm", response_model=CandidateProject, summary="Confirm and promote project candidate to profile")
async def confirm_project_candidate(
    auth: AuthDep,
    candidate_id: str,
    req: ConfirmCandidateRequest,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> CandidateProject:
    try:
        return svc.confirm_project_candidate(
            candidate_id=candidate_id,
            profile_id=req.profile_id,
            modified_data=req.modified_data,
        )
    except Exception as exc:
        raise _map_exception(exc) from exc


@router.post("/candidates/{candidate_id}/reject", summary="Reject candidate skill or project")
async def reject_candidate(
    auth: AuthDep,
    candidate_id: str,
    svc: GitHubIntelligenceService = Depends(get_github_service),
) -> dict[str, Any]:
    try:
        svc.reject_candidate(candidate_id)
        return {"status": "rejected", "candidate_id": candidate_id}
    except Exception as exc:
        raise _map_exception(exc) from exc
