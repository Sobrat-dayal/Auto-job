"""Repository Detailed Metadata & Language Analysis Synchronization (Stage 22)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Optional

from app.recruitment.github.auth.connection import GitHubConnectionManager
from app.recruitment.github.client.rest import GitHubRestClient
from app.recruitment.github.contracts import RepositoryMetadata, SyncStatus
from app.recruitment.github.repositories.discovery import RepositoryDiscoveryService

logger = logging.getLogger("autonom.recruitment.github.repositories.metadata")


class RepositoryMetadataSync:
    """Synchronizes language byte distributions, topics, and pins default branch commit SHA."""

    def __init__(self, conn_mgr: GitHubConnectionManager, discovery: RepositoryDiscoveryService) -> None:
        self.conn_mgr = conn_mgr
        self.discovery = discovery

    async def sync_metadata(self, repo_id: str) -> RepositoryMetadata:
        repo = self.discovery.get_repository(repo_id)
        token = self.conn_mgr.get_active_token(repo.connection_id) if repo.connection_id else None
        client = GitHubRestClient(access_token=token)

        # 1. Fetch language byte statistics
        try:
            languages = await client.get(f"/repos/{repo.owner}/{repo.name}/languages")
            if isinstance(languages, dict):
                repo.languages = languages
        except Exception as exc:
            logger.warning(f"Could not fetch language stats for '{repo.full_name}': {exc}")

        # 2. Fetch topics
        try:
            topics_data = await client.get(f"/repos/{repo.owner}/{repo.name}/topics")
            if isinstance(topics_data, dict) and "names" in topics_data:
                repo.topics = topics_data["names"]
        except Exception as exc:
            logger.debug(f"Could not fetch topics for '{repo.full_name}': {exc}")

        # 3. Resolve commit SHA on default branch
        try:
            commit_data = await client.get(f"/repos/{repo.owner}/{repo.name}/commits/{repo.default_branch}")
            if isinstance(commit_data, dict) and "sha" in commit_data:
                repo.current_commit_sha = commit_data["sha"]
        except Exception as exc:
            logger.warning(f"Could not resolve head commit SHA on '{repo.default_branch}' for '{repo.full_name}': {exc}")

        repo.sync_status = SyncStatus.COMPLETED
        repo.last_synced_at = datetime.now(UTC)
        return repo
