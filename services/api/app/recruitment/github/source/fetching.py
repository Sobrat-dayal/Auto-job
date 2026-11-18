"""Targeted Source Code & Manifest Fetching with Secret Redaction (Stage 22)."""

from __future__ import annotations

import base64
import logging
from typing import Optional

from app.recruitment.github.auth.connection import GitHubConnectionManager
from app.recruitment.github.client.rest import GitHubRestClient
from app.recruitment.github.contracts import FileContentSnippet
from app.recruitment.github.errors import GitHubSourceAnalysisError
from app.recruitment.github.repositories.discovery import RepositoryDiscoveryService
from app.recruitment.github.source.filters import MAX_FILE_SIZE_BYTES
from app.recruitment.github.source.secrets import SecretRedactor

logger = logging.getLogger("autonom.recruitment.github.source.fetching")


class SourceFetcher:
    """Fetches targeted file contents, extracts text, enforces limits, and redacts secrets."""

    def __init__(self, conn_mgr: GitHubConnectionManager, discovery: RepositoryDiscoveryService) -> None:
        self.conn_mgr = conn_mgr
        self.discovery = discovery

    async def fetch_file(self, repo_id: str, path: str, commit_sha: Optional[str] = None) -> FileContentSnippet:
        repo = self.discovery.get_repository(repo_id)
        token = self.conn_mgr.get_active_token(repo.connection_id) if repo.connection_id else None
        client = GitHubRestClient(access_token=token)

        ref = commit_sha or repo.current_commit_sha or repo.default_branch
        endpoint = f"/repos/{repo.owner}/{repo.name}/contents/{path}?ref={ref}"

        try:
            data = await client.get(endpoint)
        except Exception as exc:
            logger.error(f"Failed to fetch file '{path}' in '{repo.full_name}': {exc}")
            raise GitHubSourceAnalysisError(f"Could not fetch file '{path}': {exc}") from exc

        if not isinstance(data, dict) or "content" not in data:
            raise GitHubSourceAnalysisError(f"Expected file content dictionary for '{path}'.")

        raw_size = data.get("size", 0)
        encoding = data.get("encoding", "base64")
        content_bytes = b""
        if encoding == "base64" and data.get("content"):
            content_bytes = base64.b64decode(data["content"])

        is_truncated = False
        if len(content_bytes) > MAX_FILE_SIZE_BYTES:
            content_bytes = content_bytes[:MAX_FILE_SIZE_BYTES]
            is_truncated = True

        raw_text = content_bytes.decode("utf-8", errors="replace")
        sanitized_text, has_redacted = SecretRedactor.redact(raw_text)

        return FileContentSnippet(
            repo_id=repo_id,
            path=path,
            sha=data.get("sha", ""),
            size_bytes=raw_size,
            content=sanitized_text,
            is_truncated=is_truncated,
            has_redacted_secrets=has_redacted,
        )
