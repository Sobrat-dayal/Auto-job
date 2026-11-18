"""Git Tree Inspection & Directory Hierarchy Analysis (Stage 22)."""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from app.recruitment.github.auth.connection import GitHubConnectionManager
from app.recruitment.github.client.rest import GitHubRestClient
from app.recruitment.github.contracts import SourceTreeEntry
from app.recruitment.github.repositories.discovery import RepositoryDiscoveryService
from app.recruitment.github.source.filters import SourceFilter

logger = logging.getLogger("autonom.recruitment.github.source.trees")


class SourceTreeInspector:
    """Retrieves full repository file hierarchies and identifies candidate code modules."""

    def __init__(self, conn_mgr: GitHubConnectionManager, discovery: RepositoryDiscoveryService) -> None:
        self.conn_mgr = conn_mgr
        self.discovery = discovery

    async def inspect_tree(self, repo_id: str) -> list[SourceTreeEntry]:
        repo = self.discovery.get_repository(repo_id)
        token = self.conn_mgr.get_active_token(repo.connection_id) if repo.connection_id else None
        client = GitHubRestClient(access_token=token)

        commit_sha = repo.current_commit_sha or repo.default_branch
        endpoint = f"/repos/{repo.owner}/{repo.name}/git/trees/{commit_sha}?recursive=1"

        try:
            tree_data = await client.get(endpoint)
        except Exception as exc:
            logger.warning(f"Recursive git tree fetch failed for '{repo.full_name}': {exc}")
            return []

        raw_entries = tree_data.get("tree", []) if isinstance(tree_data, dict) else []
        entries: list[SourceTreeEntry] = []

        for item in raw_entries:
            path_str = item.get("path", "")
            if not path_str or SourceFilter.should_ignore_path(path_str):
                continue

            ext = Path(path_str).suffix.lstrip(".").lower()
            entry = SourceTreeEntry(
                path=path_str,
                mode=item.get("mode", "100644"),
                type=item.get("type", "blob"),
                sha=item.get("sha", ""),
                size=item.get("size"),
                is_binary=False,
                is_vendored=False,
                language=ext or None,
            )
            entries.append(entry)

        logger.info(f"Retrieved {len(entries)} candidate source entries for '{repo.full_name}'.")
        return entries
