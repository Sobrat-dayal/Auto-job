"""Stage 22 GitHub Account Integration & Technical Portfolio Intelligence Contracts."""

from __future__ import annotations

from datetime import UTC, datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class ConnectionMode(str, Enum):
    PUBLIC_ONLY = "public_only"
    AUTHORIZED_APP = "authorized_app"
    PERSONAL_ACCESS_TOKEN = "personal_access_token"
    MANUAL_URL = "manual_url"


class ConnectionStatus(str, Enum):
    CONNECTED = "connected"
    NOT_CONNECTED = "not_connected"
    EXPIRED = "expired"
    REVOKED = "revoked"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"


class RepoVisibility(str, Enum):
    PUBLIC = "public"
    PRIVATE = "private"
    INTERNAL = "internal"


class SyncStatus(str, Enum):
    NOT_SYNCED = "not_synced"
    QUEUED = "queued"
    SYNCING = "syncing"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    RATE_LIMITED = "rate_limited"
    AUTHENTICATION_REQUIRED = "authentication_required"
    PERMISSION_DENIED = "permission_denied"
    REPOSITORY_UNAVAILABLE = "repository_unavailable"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TechCategory(str, Enum):
    PROGRAMMING_LANGUAGE = "programming_language"
    FRAMEWORK = "framework"
    LIBRARY = "library"
    DATABASE = "database"
    ORM = "orm"
    TESTING = "testing"
    BUILD_TOOL = "build_tool"
    PACKAGE_MANAGER = "package_manager"
    CI_CD = "ci_cd"
    CLOUD = "cloud"
    CONTAINERIZATION = "containerization"
    AI_ML = "ai_ml"
    OTHER = "other"


class DetectionConfidence(str, Enum):
    DETECTED = "detected"
    STRONGLY_SUPPORTED = "strongly_supported"
    WEAK_SIGNAL = "weak_signal"
    UNCERTAIN = "uncertain"


class ArchitectureType(str, Enum):
    MONOREPO = "monorepo"
    MICROSERVICES = "microservices"
    FRONTEND_ONLY = "frontend_only"
    BACKEND_API = "backend_api"
    CLI_TOOL = "cli_tool"
    LIBRARY_PACKAGE = "library_package"
    FULLSTACK_APPLICATION = "fullstack_application"
    DATA_PIPELINE = "data_pipeline"
    OTHER = "other"


class AttributionLevel(str, Enum):
    REPOSITORY_ASSOCIATED = "repository_associated"
    ACCOUNT_ATTRIBUTED_ACTIVITY = "account_attributed_activity"
    COMMIT_AUTHOR_EVIDENCE = "commit_author_evidence"
    CONTRIBUTION_EVIDENCE = "contribution_evidence"
    APPLICANT_CONFIRMED_CONTRIBUTION = "applicant_confirmed_contribution"
    INDEPENDENTLY_CORROBORATED = "independently_corroborated"


class CandidateStatus(str, Enum):
    AWAITING_REVIEW = "awaiting_review"
    CONFIRMED = "confirmed"
    REJECTED = "rejected"
    MODIFIED = "modified"


# =============================================================================
# Connection & Account Models
# =============================================================================

class GitHubConnection(BaseModel):
    id: str = Field(default_factory=lambda: f"ghc_{uuid4().hex[:12]}")
    profile_id: str = Field(default="prof_primary_applicant")
    owner_id: str = Field(default="default_user")
    mode: ConnectionMode = Field(default=ConnectionMode.PUBLIC_ONLY)
    github_user_id: Optional[str] = None
    login: str = Field(description="GitHub login / username")
    display_name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: Optional[str] = None
    profile_url: str = Field(default="", description="Web URL to public GitHub profile")
    scopes: list[str] = Field(default_factory=list)
    can_access_private: bool = Field(default=False)
    public_repos_count: int = Field(default=0)
    followers_count: int = Field(default=0)
    token_reference_id: Optional[str] = Field(default=None, description="DPAPI vault secret reference")
    status: ConnectionStatus = Field(default=ConnectionStatus.NOT_CONNECTED)
    rate_limit_remaining: int = Field(default=60)
    rate_limit_limit: int = Field(default=60)
    rate_limit_reset: Optional[int] = None
    connected_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_validated_at: Optional[datetime] = None
    selected_repo_count: int = Field(default=0)


class GitHubConnectionCreateRequest(BaseModel):
    mode: ConnectionMode = Field(default=ConnectionMode.PUBLIC_ONLY)
    username: str = Field(description="GitHub handle or organization name")
    access_token: Optional[str] = Field(default=None, description="Fine-grained or classic read-only token")
    profile_id: Optional[str] = Field(default=None)


class GitHubPermissionReport(BaseModel):
    connection_id: str
    mode: ConnectionMode
    scopes_granted: list[str]
    can_read_public_repos: bool = True
    can_read_private_repos: bool = False
    can_read_org_repos: bool = False
    rate_limit_remaining: int = 60
    rate_limit_reset: Optional[int] = None


# =============================================================================
# Repository Models
# =============================================================================

class RepositoryMetadata(BaseModel):
    id: str = Field(default_factory=lambda: f"ghr_{uuid4().hex[:12]}")
    github_repo_id: int = 0
    connection_id: Optional[str] = None
    owner: str
    name: str
    full_name: str
    description: Optional[str] = None
    url: str = ""
    html_url: str = ""
    clone_url: Optional[str] = None
    visibility: RepoVisibility = Field(default=RepoVisibility.PUBLIC)
    is_fork: bool = False
    parent_repo: Optional[str] = None
    parent_repo_full_name: Optional[str] = None
    is_archived: bool = False
    is_disabled: bool = False
    is_template: bool = False
    default_branch: str = "main"
    current_commit_sha: Optional[str] = None
    default_branch_commit_sha: Optional[str] = None
    topics: list[str] = Field(default_factory=list)
    primary_language: Optional[str] = None
    languages: dict[str, int] = Field(default_factory=dict, description="Language byte distribution")
    license_spdx: Optional[str] = None
    size_kb: int = 0
    stars_count: int = 0
    stargazers_count: int = 0
    forks_count: int = 0
    open_issues_count: int = 0
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    pushed_at: Optional[str] = None
    is_selected: bool = False
    allow_source_inspection: bool = False
    sync_status: SyncStatus = Field(default=SyncStatus.NOT_SYNCED)
    last_synced_at: Optional[datetime] = None


class RepositorySelectionRequest(BaseModel):
    is_selected: bool = True
    allow_source_inspection: bool = True


# =============================================================================
# Source Tree & File Analysis Models
# =============================================================================

class SourceTreeEntry(BaseModel):
    path: str
    mode: str = "100644"
    type: str = "blob"  # blob or tree
    sha: str
    size: Optional[int] = None
    is_binary: bool = False
    is_vendored: bool = False
    is_generated: bool = False
    language: Optional[str] = None


class FileContentSnippet(BaseModel):
    repo_id: str
    path: str
    sha: str
    size_bytes: int
    content: str
    is_truncated: bool = False
    has_redacted_secrets: bool = False


# =============================================================================
# Technology Findings & Architecture
# =============================================================================

class TechnologyFinding(BaseModel):
    id: str = Field(default_factory=lambda: f"thf_{uuid4().hex[:8]}")
    repo_id: str = ""
    technology_name: str = ""
    canonical_name: str = ""
    name: str = ""
    category: TechCategory = TechCategory.OTHER
    confidence: DetectionConfidence = Field(default=DetectionConfidence.DETECTED)
    evidence_type: str = "manifest_dependency"
    source_file: str = ""
    evidence_source: str = ""
    source_excerpt: Optional[str] = None
    version_spec: Optional[str] = None
    version: Optional[str] = None
    is_dev_dependency: bool = False

    def model_post_init(self, __context: Any) -> None:
        if self.name and not self.technology_name:
            self.technology_name = self.name
        if self.technology_name and not self.name:
            self.name = self.technology_name
        if not self.canonical_name:
            self.canonical_name = self.name or self.technology_name
        if self.version and not self.version_spec:
            self.version_spec = self.version
        if self.version_spec and not self.version:
            self.version = self.version_spec
        if self.evidence_source and not self.source_file:
            self.source_file = self.evidence_source
        if self.source_file and not self.evidence_source:
            self.evidence_source = self.source_file


class RepositoryArchitecture(BaseModel):
    repo_id: str
    architecture_type: ArchitectureType = Field(default=ArchitectureType.OTHER)
    has_frontend: bool = False
    has_backend: bool = False
    has_tests: bool = False
    has_ci: bool = False
    has_docker: bool = False
    has_docs: bool = False
    structure_summary: str = Field(default="Standard codebase structure")
    entrypoints: list[str] = Field(default_factory=list)
    key_directories: list[str] = Field(default_factory=list)


# =============================================================================
# Contributions & Attribution
# =============================================================================

class CommitEvidence(BaseModel):
    sha: str = ""
    commit_sha: str = ""
    repo_id: str = ""
    author_name: str = ""
    author_email: str = ""
    author_date: str = ""
    committed_date: str = ""
    author_login: Optional[str] = None
    committer_name: Optional[str] = None
    committer_date: Optional[str] = None
    message: str = ""
    is_merge: bool = False
    is_squash: bool = False
    additions: int = 0
    deletions: int = 0
    total_changes: int = 0
    files_changed: list[str] = Field(default_factory=list)
    attribution_level: AttributionLevel = Field(default=AttributionLevel.REPOSITORY_ASSOCIATED)
    is_applicant_attributed: bool = False
    is_applicant: bool = False
    is_bot: bool = False

    def model_post_init(self, __context: Any) -> None:
        if self.sha and not self.commit_sha:
            self.commit_sha = self.sha
        if self.commit_sha and not self.sha:
            self.sha = self.commit_sha
        if self.author_date and not self.committed_date:
            self.committed_date = self.author_date
        if self.committed_date and not self.author_date:
            self.author_date = self.committed_date
        if self.is_applicant and not self.is_applicant_attributed:
            self.is_applicant_attributed = self.is_applicant
        if self.is_applicant_attributed and not self.is_applicant:
            self.is_applicant = self.is_applicant_attributed


class PullRequestEvidence(BaseModel):
    pr_number: int
    repo_id: str
    title: str
    description: Optional[str] = None
    author_login: str
    state: str = "closed"
    merged: bool = False
    merged_at: Optional[str] = None
    merged_by: Optional[str] = None
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    attribution_level: AttributionLevel = Field(default=AttributionLevel.REPOSITORY_ASSOCIATED)
    is_applicant_attributed: bool = False
    is_applicant: bool = False

    def model_post_init(self, __context: Any) -> None:
        if self.is_applicant and not self.is_applicant_attributed:
            self.is_applicant_attributed = self.is_applicant
        if self.is_applicant_attributed and not self.is_applicant:
            self.is_applicant = self.is_applicant_attributed


class ContributionFinding(BaseModel):
    id: str = Field(default_factory=lambda: f"ctf_{uuid4().hex[:8]}")
    repo_id: str
    repo_name: str = ""
    activity_type: str = "commit"
    reference_id: str = ""
    summary: str
    attribution_level: AttributionLevel = Field(default=AttributionLevel.REPOSITORY_ASSOCIATED)
    total_commits_found: int = 0
    applicant_commits_count: int = 0
    pull_requests_count: int = 0
    evidence_refs: list[str] = Field(default_factory=list)
    is_user_confirmed: bool = False
    confirmed_role_description: Optional[str] = None
    timestamp: Optional[str] = None


# =============================================================================
# Candidate Generation (Skills & Projects)
# =============================================================================

class CandidateSkill(BaseModel):
    id: str = Field(default_factory=lambda: f"gsk_{uuid4().hex[:8]}")
    repo_id: str = ""
    repo_name: str = ""
    name: str = ""
    canonical_name: str = ""
    category: Any = "other"
    proficiency_estimate: str = "intermediate"
    proficiency_hint: str = "intermediate"
    version: Optional[str] = None
    evidence_repo_id: str = ""
    evidence_repo_name: str = ""
    evidence_file_path: Optional[str] = None
    confidence: DetectionConfidence = DetectionConfidence.DETECTED
    years_evidence: Optional[float] = None
    evidence_refs: list[str] = Field(default_factory=list)
    source_files: list[str] = Field(default_factory=list)
    status: CandidateStatus = Field(default=CandidateStatus.AWAITING_REVIEW)
    confirmed_skill_id: Optional[str] = None
    user_note: Optional[str] = None

    def model_post_init(self, __context: Any) -> None:
        if not self.canonical_name:
            self.canonical_name = self.name
        if self.evidence_repo_id and not self.repo_id:
            self.repo_id = self.evidence_repo_id
        if self.repo_id and not self.evidence_repo_id:
            self.evidence_repo_id = self.repo_id
        if self.evidence_repo_name and not self.repo_name:
            self.repo_name = self.evidence_repo_name
        if self.repo_name and not self.evidence_repo_name:
            self.evidence_repo_name = self.repo_name
        if self.proficiency_hint and not self.proficiency_estimate:
            self.proficiency_estimate = self.proficiency_hint
        if self.proficiency_estimate and not self.proficiency_hint:
            self.proficiency_hint = self.proficiency_estimate


class CandidateProject(BaseModel):
    id: str = Field(default_factory=lambda: f"gpj_{uuid4().hex[:8]}")
    repo_id: str = ""
    repo_name: str = ""
    title: str = ""
    description: str = ""
    technologies: list[str] = Field(default_factory=list)
    suggested_contribution: str = ""
    repo_url: str = ""
    architecture_type: ArchitectureType = ArchitectureType.OTHER
    stars: int = 0
    is_fork: bool = False
    visibility: RepoVisibility = Field(default=RepoVisibility.PUBLIC)
    evidence_refs: list[str] = Field(default_factory=list)
    status: CandidateStatus = Field(default=CandidateStatus.AWAITING_REVIEW)
    confirmed_project_id: Optional[str] = None
    user_note: Optional[str] = None


class CandidateReviewActionRequest(BaseModel):
    action: str = Field(..., description="confirm, modify, reject")
    modified_data: Optional[dict[str, Any]] = None
    notes: Optional[str] = None


# =============================================================================
# Synchronization, Jobs & Diagnostics
# =============================================================================

class SyncJobRecord(BaseModel):
    job_id: str = Field(default_factory=lambda: f"sjb_{uuid4().hex[:12]}")
    repo_id: str
    repo_name: str
    sync_type: str = "full"  # metadata, tree, full
    status: SyncStatus = Field(default=SyncStatus.QUEUED)
    files_analyzed: int = 0
    files_skipped: int = 0
    bytes_analyzed: int = 0
    api_calls_made: int = 0
    error_message: Optional[str] = None
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: Optional[datetime] = None


class GitHubDiagnostics(BaseModel):
    total_connections: int = 0
    active_connection_user: Optional[str] = None
    total_discovered_repositories: int = 0
    total_selected_repositories: int = 0
    total_analyzed_repositories: int = 0
    rate_limit_remaining: int = 60
    rate_limit_limit: int = 60
    pending_skill_candidates: int = 0
    pending_project_candidates: int = 0
    confirmed_claims_count: int = 0
    cached_etag_entries: int = 0
    sync_error_count: int = 0
