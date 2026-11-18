"""GitHub Connection Lifecycle and Token Management (Stage 22)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Optional
from uuid import uuid4

from app.recruitment.github.client.rest import GitHubRestClient
from app.recruitment.github.contracts import (
    ConnectionMode,
    ConnectionStatus,
    GitHubConnection,
    GitHubPermissionReport,
)
from app.recruitment.github.errors import (
    GitHubAuthenticationError,
    GitHubConnectionNotFoundError,
)
from app.security.credentials import credential_manager

logger = logging.getLogger("autonom.recruitment.github.auth")


class GitHubConnectionManager:
    """Manages GitHub account connections, credential storage via DPAPI vault, and token lifecycle."""

    def __init__(self) -> None:
        self._connections: dict[str, GitHubConnection] = {}
        self._encrypted_tokens: dict[str, str] = {}  # token_reference_id -> encrypted_blob

    async def connect_account(
        self,
        login_or_username: str,
        mode: ConnectionMode = ConnectionMode.PUBLIC_ONLY,
        access_token: Optional[str] = None,
        profile_id: str = "prof_primary_applicant",
        owner_id: str = "default_user",
    ) -> GitHubConnection:
        """Establishes a verified GitHub connection and securely saves token reference."""
        token_ref: Optional[str] = None
        user_info: dict = {}
        scopes: list[str] = []

        if mode == ConnectionMode.PERSONAL_ACCESS_TOKEN and access_token:
            # Validate token against live GitHub API
            client = GitHubRestClient(access_token=access_token)
            try:
                user_info = await client.get("/user")
            except Exception as exc:
                logger.error(f"Failed to authenticate GitHub token: {exc}")
                raise GitHubAuthenticationError(f"GitHub token validation failed: {exc}") from exc

            # Encrypt token using Stage 04 DPAPI vault
            token_ref = f"tok_gh_{uuid4().hex[:12]}"
            encrypted_blob = credential_manager.encrypt_secret(access_token, provider="github")
            self._encrypted_tokens[token_ref] = encrypted_blob
            scopes = ["repo:read", "user:read"]
        else:
            # Public only mode
            client = GitHubRestClient()
            try:
                user_info = await client.get(f"/users/{login_or_username}")
            except Exception as exc:
                logger.warning(f"Could not fetch public profile for '{login_or_username}': {exc}")
                user_info = {"login": login_or_username, "html_url": f"https://github.com/{login_or_username}"}
            scopes = ["public_repo"]

        conn_id = f"ghc_{uuid4().hex[:12]}"
        conn = GitHubConnection(
            id=conn_id,
            profile_id=profile_id,
            owner_id=owner_id,
            mode=mode,
            github_user_id=str(user_info.get("id", "")) or None,
            login=user_info.get("login", login_or_username),
            display_name=user_info.get("name"),
            email=user_info.get("email"),
            avatar_url=user_info.get("avatar_url"),
            profile_url=user_info.get("html_url", f"https://github.com/{login_or_username}"),
            scopes=scopes,
            token_reference_id=token_ref,
            status=ConnectionStatus.CONNECTED,
            connected_at=datetime.now(UTC),
            last_validated_at=datetime.now(UTC),
        )
        self._connections[conn_id] = conn
        logger.info(f"Connected GitHub account '{conn.login}' in mode '{mode}'.")
        return conn

    def get_connection(self, connection_id: str) -> GitHubConnection:
        conn = self._connections.get(connection_id)
        if not conn:
            raise GitHubConnectionNotFoundError(f"GitHub connection '{connection_id}' not found.")
        return conn

    def list_connections(self, profile_id: Optional[str] = None) -> list[GitHubConnection]:
        if profile_id:
            return [c for c in self._connections.values() if c.profile_id == profile_id]
        return list(self._connections.values())

    def get_active_token(self, connection_id: str) -> Optional[str]:
        """Resolves the decrypted token using the Stage 04 DPAPI vault."""
        conn = self.get_connection(connection_id)
        if not conn.token_reference_id or conn.status != ConnectionStatus.CONNECTED:
            return None
        encrypted_blob = self._encrypted_tokens.get(conn.token_reference_id)
        if not encrypted_blob:
            return None
        return credential_manager.decrypt_secret(encrypted_blob, provider="github")

    def disconnect_connection(self, connection_id: str) -> bool:
        """Revokes local stored credentials, deletes token from vault, and marks connection REVOKED."""
        conn = self.get_connection(connection_id)
        if conn.token_reference_id and conn.token_reference_id in self._encrypted_tokens:
            del self._encrypted_tokens[conn.token_reference_id]
        conn.token_reference_id = None
        conn.status = ConnectionStatus.REVOKED
        logger.info(f"Disconnected GitHub connection '{connection_id}'.")
        return True

    def get_permission_report(self, connection_id: str) -> GitHubPermissionReport:
        conn = self.get_connection(connection_id)
        can_read_priv = "repo" in conn.scopes or "repo:read" in conn.scopes
        return GitHubPermissionReport(
            connection_id=conn.id,
            mode=conn.mode,
            scopes_granted=conn.scopes,
            can_read_public_repos=True,
            can_read_private_repos=can_read_priv,
            can_read_org_repos="read:org" in conn.scopes or can_read_priv,
            rate_limit_remaining=conn.rate_limit_remaining,
            rate_limit_reset=conn.rate_limit_reset,
        )
