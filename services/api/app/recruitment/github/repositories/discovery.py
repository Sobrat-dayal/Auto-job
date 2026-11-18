"""Repository Discovery and Ingestion for GitHub Integration (Stage 22)."""

from __future__ import annotations

import logging
import re
from typing import Optional
from uuid import uuid4

from app.recruitment.github.auth.connection import GitHubConnectionManager
from app.recruitment.github.client.rest import GitHubRestClient
from app.recruitment.github.contracts import (
    ConnectionMode,
    RepoVisibility,
    RepositoryMetadata,
    SyncStatus,
)
from app.recruitment.github.errors import (
    GitHubNotFoundError,
    GitHubRepositoryNotFoundError,
    InvalidRepositoryURLError,
)

logger = logging.getLogger("autonom.recruitment.github.repositories.discovery")

GITHUB_URL_REGEX = re.compile(
    r"^https?://(?:www\.)?github\.com/([a-zA-Z0-9_.-]+)/([a-zA-Z0-9_.-]+?)(?:\.git|/.*)?$"
)


def parse_github_repo_url(url: str) -> tuple[str, str]:
    """Extracts (owner, repo_name) from standard GitHub URLs."""
    match = GITHUB_URL_REGEX.match(url.strip())
    if not match:
        raise InvalidRepositoryURLError(f"Invalid GitHub repository URL: {url}")
    return match.group(1), match.group(2)


class RepositoryDiscoveryService:
    """Discovers accessible repositories across public profiles and authorized accounts."""

    def __init__(self, connection_manager: GitHubConnectionManager) -> None:
        self.conn_mgr = connection_manager
        self._repositories: dict[str, RepositoryMetadata] = {}  # repo_id -> metadata
        self._url_index: dict[str, str] = {}  # "owner/name" -> repo_id

    def _normalize_repo_payload(self, item: dict, connection_id: Optional[str] = None) -> RepositoryMetadata:
        repo_id = f"ghr_{uuid4().hex[:12]}"
        full_name = item.get("full_name") or f"{item.get('owner', {}).get('login', 'unknown')}/{item.get('name')}"
        if full_name.lower() in self._url_index:
            existing_id = self._url_index[full_name.lower()]
            return self._repositories[existing_id]

        owner_login = item.get("owner", {}).get("login") if isinstance(item.get("owner"), dict) else item.get("owner", "unknown")
        visibility = RepoVisibility.PRIVATE if item.get("private") else RepoVisibility.PUBLIC

        repo = RepositoryMetadata(
            id=repo_id,
            github_repo_id=item.get("id", 0),
            connection_id=connection_id,
            owner=owner_login,
            name=item.get("name", "unnamed"),
            full_name=full_name,
            description=item.get("description"),
            url=item.get("html_url", f"https://github.com/{full_name}"),
            clone_url=item.get("clone_url"),
            visibility=visibility,
            is_fork=bool(item.get("fork")),
            parent_repo_full_name=item.get("parent", {}).get("full_name") if isinstance(item.get("parent"), dict) else None,
            is_archived=bool(item.get("archived")),
            is_template=bool(item.get("is_template")),
            default_branch=item.get("default_branch") or "main",
            topics=item.get("topics") or [],
            primary_language=item.get("language"),
            license_spdx=item.get("license", {}).get("spdx_id") if isinstance(item.get("license"), dict) else None,
            size_kb=item.get("size", 0),
            stargazers_count=item.get("stargazers_count", 0),
            forks_count=item.get("forks_count", 0),
            open_issues_count=item.get("open_issues_count", 0),
            created_at=item.get("created_at"),
            updated_at=item.get("updated_at"),
            pushed_at=item.get("pushed_at"),
            sync_status=SyncStatus.NOT_SYNCED,
        )
        self._repositories[repo_id] = repo
        self._url_index[full_name.lower()] = repo_id
        return repo

    async def discover_repositories(self, connection_id: str) -> list[RepositoryMetadata]:
        """Discovers repositories accessible through a connected account."""
        conn = self.conn_mgr.get_connection(connection_id)
        token = self.conn_mgr.get_active_token(connection_id)
        client = GitHubRestClient(access_token=token)

        endpoint = "/user/repos?type=all&sort=updated" if token else f"/users/{conn.login}/repos?sort=updated"
        raw_repos = await client.get_paginated(endpoint, max_pages=3)

        discovered: list[RepositoryMetadata] = []
        for raw in raw_repos:
            repo = self._normalize_repo_payload(raw, connection_id=connection_id)
            discovered.append(repo)

        conn.selected_repo_count = len([r for r in self._repositories.values() if r.connection_id == connection_id and r.is_selected])
        return discovered

    async def ingest_public_repo_url(self, repo_url: str, connection_id: Optional[str] = None) -> RepositoryMetadata:
        """Fetches metadata for an explicitly provided public GitHub repository URL."""
        owner, repo_name = parse_github_repo_url(repo_url)
        token = self.conn_mgr.get_active_token(connection_id) if connection_id else None
        client = GitHubRestClient(access_token=token)

        try:
            raw = await client.get(f"/repos/{owner}/{repo_name}")
        except GitHubNotFoundError as exc:
            raise GitHubRepositoryNotFoundError(f"Repository '{owner}/{repo_name}' not found on GitHub.") from exc

        return self._normalize_repo_payload(raw, connection_id=connection_id)

    def get_repository(self, repo_id: str) -> RepositoryMetadata:
        repo = self._repositories.get(repo_id)
        if not repo:
            raise GitHubRepositoryNotFoundError(f"Repository '{repo_id}' not found.")
        return repo

    def list_repositories(self, connection_id: Optional[str] = None, only_selected: bool = False) -> list[RepositoryMetadata]:
        repos = list(self._repositories.values())
        if connection_id:
            repos = [r for r in repos if r.connection_id == connection_id]
        if only_selected:
            repos = [r for r in repos if r.is_selected]
        return repos

    def select_repository(self, repo_id: str, allow_source_inspection: bool = True) -> RepositoryMetadata:
        repo = self.get_repository(repo_id)
        repo.is_selected = True
        repo.allow_source_inspection = allow_source_inspection
        return repo

    def deselect_repository(self, repo_id: str) -> RepositoryMetadata:
        repo = self.get_repository(repo_id)
        repo.is_selected = False
        return repo
