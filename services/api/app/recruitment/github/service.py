"""Central GitHub & Technical Portfolio Intelligence Service Facade (Stage 22)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4

from app.recruitment.github.analysis.architecture import ArchitectureAnalyzer
from app.recruitment.github.analysis.dependencies import DependencyManifestParser
from app.recruitment.github.analysis.frameworks import TechnologyClassifier
from app.recruitment.github.auth.connection import GitHubConnectionManager
from app.recruitment.github.client.caching import ETagCacheManager
from app.recruitment.github.client.rate_limits import RateLimitController
from app.recruitment.github.client.rest import GitHubRestClient
from app.recruitment.github.contracts import (
    CandidateProject,
    CandidateSkill,
    CommitEvidence,
    ConnectionMode,
    ContributionFinding,
    GitHubConnection,
    GitHubDiagnostics,
    PullRequestEvidence,
    RepositoryArchitecture,
    RepositoryMetadata,
    SyncJobRecord,
    SyncStatus,
    TechnologyFinding,
)
from app.recruitment.github.contributions.attribution import ContributionAttributionEngine
from app.recruitment.github.evidence.candidates import (
    CandidateGenerator,
    CandidateReviewManager,
)
from app.recruitment.github.repositories.discovery import RepositoryDiscoveryService
from app.recruitment.github.repositories.metadata import RepositoryMetadataSync
from app.recruitment.github.source.fetching import SourceFetcher
from app.recruitment.github.source.filters import SourceFilter
from app.recruitment.github.source.trees import SourceTreeInspector
from app.recruitment.profile.integrations.memory import ProfileMemorySync

logger = logging.getLogger("autonom.recruitment.github.service")


class GitHubIntelligenceService:
    """Master service orchestrating GitHub connectivity, source code analysis, and profile attribution."""

    def __init__(self) -> None:
        self.rate_limiter = RateLimitController()
        self.cache_mgr = ETagCacheManager()
        self.conn_mgr = GitHubConnectionManager()
        self.discovery = RepositoryDiscoveryService(self.conn_mgr)
        self.meta_sync = RepositoryMetadataSync(self.conn_mgr, self.discovery)
        self.tree_inspector = SourceTreeInspector(self.conn_mgr, self.discovery)
        self.source_fetcher = SourceFetcher(self.conn_mgr, self.discovery)
        self.review_mgr = CandidateReviewManager()

        # In-memory storage for analysis results
        self._technologies: dict[str, list[TechnologyFinding]] = {}  # repo_id -> list
        self._architectures: dict[str, RepositoryArchitecture] = {}  # repo_id -> arch
        self._commits: dict[str, list[CommitEvidence]] = {}  # repo_id -> list
        self._prs: dict[str, list[PullRequestEvidence]] = {}  # repo_id -> list
        self._contributions: dict[str, list[ContributionFinding]] = {}  # repo_id -> list
        self._sync_jobs: dict[str, SyncJobRecord] = {}

    # =========================================================================
    # Connection Management
    # =========================================================================

    async def connect_account(
        self,
        username: str,
        mode: ConnectionMode = ConnectionMode.PUBLIC_ONLY,
        access_token: Optional[str] = None,
        profile_id: str = "prof_primary_applicant",
    ) -> GitHubConnection:
        conn = await self.conn_mgr.connect_account(
            login_or_username=username,
            mode=mode,
            access_token=access_token,
            profile_id=profile_id,
        )
        await ProfileMemorySync.publish_event(
            "github.connected",
            profile_id,
            {"connection_id": conn.id, "login": conn.login, "mode": conn.mode.value},
        )
        return conn

    def list_connections(self, profile_id: Optional[str] = None) -> list[GitHubConnection]:
        return self.conn_mgr.list_connections(profile_id=profile_id)

    def get_connection(self, connection_id: str) -> GitHubConnection:
        return self.conn_mgr.get_connection(connection_id)

    def disconnect(self, connection_id: str) -> bool:
        conn = self.conn_mgr.get_connection(connection_id)
        res = self.conn_mgr.disconnect_connection(connection_id)
        self.cache_mgr.invalidate()
        return res

    # =========================================================================
    # Repository Discovery & Selection
    # =========================================================================

    async def discover_repositories(self, connection_id: str) -> list[RepositoryMetadata]:
        return await self.discovery.discover_repositories(connection_id)

    async def add_manual_repository(self, url: str, connection_id: Optional[str] = None) -> RepositoryMetadata:
        return await self.discovery.ingest_public_repo_url(url, connection_id=connection_id)

    def list_repositories(self, connection_id: Optional[str] = None, only_selected: bool = False) -> list[RepositoryMetadata]:
        return self.discovery.list_repositories(connection_id, only_selected)

    def get_repository(self, repo_id: str) -> RepositoryMetadata:
        return self.discovery.get_repository(repo_id)

    def select_repository(self, repo_id: str, allow_source_inspection: bool = True) -> RepositoryMetadata:
        repo = self.discovery.select_repository(repo_id, allow_source_inspection)
        return repo

    def deselect_repository(self, repo_id: str) -> RepositoryMetadata:
        return self.discovery.deselect_repository(repo_id)

    # =========================================================================
    # End-to-End Repository Analysis
    # =========================================================================

    async def analyze_repository(self, repo_id: str) -> SyncJobRecord:
        """Executes full multi-stage analysis: metadata, tree, dependencies, architecture, contributions."""
        repo = self.discovery.get_repository(repo_id)
        job_id = f"sjb_{uuid4().hex[:12]}"
        job = SyncJobRecord(
            job_id=job_id,
            repo_id=repo_id,
            repo_name=repo.name,
            status=SyncStatus.SYNCING,
            started_at=datetime.now(UTC),
        )
        self._sync_jobs[job_id] = job
        repo.sync_status = SyncStatus.SYNCING

        try:
            # 1. Sync Detailed Metadata (languages, topics, default commit)
            await self.meta_sync.sync_metadata(repo_id)
            job.api_calls_made += 3

            # 2. Inspect Git Tree
            entries = await self.tree_inspector.inspect_tree(repo_id)
            job.api_calls_made += 1
            job.files_analyzed = len(entries)

            # 3. Analyze Architecture & Layout
            arch, arch_findings = ArchitectureAnalyzer.analyze_layout(repo_id, entries)
            self._architectures[repo_id] = arch

            # 4. Fetch and Parse Dependency Manifests
            findings: list[TechnologyFinding] = list(arch_findings)
            manifest_entries = [e for e in entries if SourceFilter.is_manifest_file(e.path)][:10]

            for m in manifest_entries:
                try:
                    file_snippet = await self.source_fetcher.fetch_file(repo_id, m.path)
                    job.api_calls_made += 1
                    job.bytes_analyzed += file_snippet.size_bytes
                    parsed = DependencyManifestParser.parse_manifest(repo_id, m.path, file_snippet.content)
                    findings.extend(parsed)
                except Exception as exc:
                    logger.debug(f"Manifest parse skipped for '{m.path}': {exc}")

            # Classify all technology findings
            classified_techs = TechnologyClassifier.classify_findings(findings)
            self._technologies[repo_id] = classified_techs

            # 5. Contribution & Attribution Analysis
            token = self.conn_mgr.get_active_token(repo.connection_id) if repo.connection_id else None
            client = GitHubRestClient(access_token=token)

            applicant_login = ""
            if repo.connection_id:
                try:
                    conn = self.conn_mgr.get_connection(repo.connection_id)
                    applicant_login = conn.login
                except Exception:
                    pass

            # Fetch commits
            try:
                raw_commits = await client.get_paginated(f"/repos/{repo.owner}/{repo.name}/commits", max_pages=1)
                job.api_calls_made += 1
                commit_evs = ContributionAttributionEngine.evaluate_commits(repo, raw_commits, applicant_login)
                self._commits[repo_id] = commit_evs
            except Exception as exc:
                logger.warning(f"Could not fetch commits for '{repo.full_name}': {exc}")
                commit_evs = []

            # Fetch PRs
            try:
                raw_prs = await client.get_paginated(f"/repos/{repo.owner}/{repo.name}/pulls?state=all", max_pages=1)
                job.api_calls_made += 1
                pr_evs = ContributionAttributionEngine.evaluate_pull_requests(repo, raw_prs, applicant_login)
                self._prs[repo_id] = pr_evs
            except Exception as exc:
                logger.debug(f"Could not fetch PRs for '{repo.full_name}': {exc}")
                pr_evs = []

            contributions = ContributionAttributionEngine.generate_contribution_findings(repo, commit_evs, pr_evs)
            self._contributions[repo_id] = contributions

            # 6. Generate Skill & Project Candidates
            candidate_skills = CandidateGenerator.generate_skill_candidates(repo, classified_techs)
            self.review_mgr.register_skills(candidate_skills)

            candidate_project = CandidateGenerator.generate_project_candidate(repo, classified_techs, arch)
            self.review_mgr.register_project(candidate_project)

            # Finalize Job
            job.status = SyncStatus.COMPLETED
            job.completed_at = datetime.now(UTC)
            repo.sync_status = SyncStatus.COMPLETED
            repo.last_synced_at = datetime.now(UTC)

            await ProfileMemorySync.publish_event(
                "github.analysis_completed",
                repo.connection_id or "default",
                {
                    "repo_id": repo.id,
                    "repo_name": repo.name,
                    "technologies_count": len(classified_techs),
                    "candidate_skills": len(candidate_skills),
                },
            )

        except Exception as exc:
            logger.error(f"Analysis job failed for '{repo.full_name}': {exc}")
            job.status = SyncStatus.FAILED
            job.error_message = str(exc)
            job.completed_at = datetime.now(UTC)
            repo.sync_status = SyncStatus.FAILED

        return job

    # =========================================================================
    # Findings Query Methods
    # =========================================================================

    def get_technologies(self, repo_id: str) -> list[TechnologyFinding]:
        return self._technologies.get(repo_id, [])

    def get_architecture(self, repo_id: str) -> Optional[RepositoryArchitecture]:
        return self._architectures.get(repo_id)

    def get_contributions(self, repo_id: str) -> list[ContributionFinding]:
        return self._contributions.get(repo_id, [])

    def get_commits(self, repo_id: str) -> list[CommitEvidence]:
        return self._commits.get(repo_id, [])

    def get_pull_requests(self, repo_id: str) -> list[PullRequestEvidence]:
        return self._prs.get(repo_id, [])

    def list_skill_candidates(self, repo_id: Optional[str] = None) -> list[CandidateSkill]:
        return self.review_mgr.list_skill_candidates(repo_id)

    def list_project_candidates(self, repo_id: Optional[str] = None) -> list[CandidateProject]:
        return self.review_mgr.list_project_candidates(repo_id)

    def confirm_skill_candidate(
        self, candidate_id: str, profile_id: str = "prof_primary_applicant", modified_data: Optional[dict[str, Any]] = None
    ) -> CandidateSkill:
        return self.review_mgr.confirm_skill(candidate_id, profile_id, modified_data)

    def confirm_project_candidate(
        self, candidate_id: str, profile_id: str = "prof_primary_applicant", modified_data: Optional[dict[str, Any]] = None
    ) -> CandidateProject:
        return self.review_mgr.confirm_project(candidate_id, profile_id, modified_data)

    def reject_candidate(self, candidate_id: str) -> None:
        self.review_mgr.reject_candidate(candidate_id)

    def get_sync_job(self, job_id: str) -> Optional[SyncJobRecord]:
        return self._sync_jobs.get(job_id)

    def list_sync_jobs(self, repo_id: Optional[str] = None) -> list[SyncJobRecord]:
        jobs = list(self._sync_jobs.values())
        if repo_id:
            jobs = [j for j in jobs if j.repo_id == repo_id]
        return sorted(jobs, key=lambda j: j.started_at, reverse=True)

    def get_diagnostics(self) -> GitHubDiagnostics:
        conns = list(self.conn_mgr.list_connections())
        active_user = conns[0].login if conns else None
        repos = list(self.discovery.list_repositories())
        selected = [r for r in repos if r.is_selected]
        analyzed = [r for r in repos if r.sync_status == SyncStatus.COMPLETED]
        pending_skills = len([s for s in self.review_mgr.list_skill_candidates() if s.status.value == "awaiting_review"])
        pending_projects = len([p for p in self.review_mgr.list_project_candidates() if p.status.value == "awaiting_review"])
        confirmed_count = len([s for s in self.review_mgr.list_skill_candidates() if s.status.value == "confirmed"])

        return GitHubDiagnostics(
            total_connections=len(conns),
            active_connection_user=active_user,
            total_discovered_repositories=len(repos),
            total_selected_repositories=len(selected),
            total_analyzed_repositories=len(analyzed),
            rate_limit_remaining=self.rate_limiter.remaining,
            rate_limit_limit=self.rate_limiter.limit,
            pending_skill_candidates=pending_skills,
            pending_project_candidates=pending_projects,
            confirmed_claims_count=confirmed_count,
            cached_etag_entries=self.cache_mgr.entry_count,
            sync_error_count=len([j for j in self._sync_jobs.values() if j.status == SyncStatus.FAILED]),
        )


# Singleton instance
github_service = GitHubIntelligenceService()


def get_github_service() -> GitHubIntelligenceService:
    """Returns singleton instance of GitHubIntelligenceService."""
    return github_service
