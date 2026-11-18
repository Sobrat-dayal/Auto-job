"""Typed GitHub REST API Client (Stage 22)."""

from __future__ import annotations

import logging
import re
from typing import Any, Optional

import httpx

from app.recruitment.github.client.caching import ETagCacheManager
from app.recruitment.github.client.rate_limits import RateLimitController
from app.recruitment.github.errors import (
    GitHubAuthenticationError,
    GitHubNotFoundError,
    GitHubPermissionDeniedError,
    GitHubRateLimitExceededError,
)

logger = logging.getLogger("autonom.recruitment.github.client")

GITHUB_API_BASE = "https://api.github.com"
GITHUB_API_VERSION = "2022-11-28"

TOKEN_PATTERN = re.compile(r"(ghp_[A-Za-z0-9]{36,}|gho_[A-Za-z0-9]{36,}|Bearer\s+[A-Za-z0-9_.-]+)")


def redact_token_string(text: str) -> str:
    return TOKEN_PATTERN.sub("[REDACTED_GITHUB_TOKEN]", text)


class GitHubRestClient:
    """Enterprise-grade GitHub REST client with rate-limiting, ETag caching, and secret redaction."""

    def __init__(
        self,
        access_token: Optional[str] = None,
        rate_limiter: Optional[RateLimitController] = None,
        cache_manager: Optional[ETagCacheManager] = None,
        custom_base_url: str = GITHUB_API_BASE,
    ) -> None:
        self.access_token = access_token
        self.base_url = custom_base_url.rstrip("/")
        self.rate_limiter = rate_limiter or RateLimitController()
        self.cache_manager = cache_manager or ETagCacheManager()

    def _get_headers(self, etag: Optional[str] = None) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": GITHUB_API_VERSION,
            "User-Agent": "AUTONOM-Recruitment-Intelligence/1.0",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        if etag:
            headers["If-None-Match"] = etag
        return headers

    async def get(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        use_cache: bool = True,
    ) -> Any:
        """Executes GET request with rate-limit preflight check and conditional ETag caching."""
        self.rate_limiter.check_preflight()
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        cache_key = f"{endpoint}?{sorted(params.items()) if params else ''}"

        cached_etag = self.cache_manager.get_etag(cache_key) if use_cache else None
        headers = self._get_headers(etag=cached_etag)

        try:
            async with httpx.AsyncClient(timeout=20.0) as client:
                res = await client.get(url, headers=headers, params=params)
        except httpx.RequestError as exc:
            safe_msg = redact_token_string(str(exc))
            logger.error(f"GitHub connection error: {safe_msg}")
            raise GitHubNotFoundError(f"Failed to communicate with GitHub API: {safe_msg}") from exc

        # Update rate limits from response headers
        self.rate_limiter.update_from_headers(dict(res.headers))

        # Handle 304 Not Modified
        if res.status_code == 304 and use_cache:
            cached_data = self.cache_manager.get_data(cache_key)
            if cached_data is not None:
                return cached_data

        # Handle errors
        if res.status_code == 401:
            raise GitHubAuthenticationError("GitHub authentication failed. Token may be invalid or expired.")
        if res.status_code == 403:
            reset_ts = self.rate_limiter.reset_timestamp
            if "rate limit" in res.text.lower():
                raise GitHubRateLimitExceededError(
                    f"GitHub API rate limit exceeded. Reset at {reset_ts}.", reset_timestamp=reset_ts
                )
            raise GitHubPermissionDeniedError(f"GitHub permission denied: {res.text}")
        if res.status_code == 404:
            raise GitHubNotFoundError(f"Resource not found on GitHub: {endpoint}")
        if res.status_code >= 400:
            raise GitHubNotFoundError(f"GitHub API returned error {res.status_code}: {res.text}")

        data = res.json()
        etag = res.headers.get("etag")
        if etag and use_cache:
            self.cache_manager.set(cache_key, etag, data)

        return data

    async def get_paginated(
        self,
        endpoint: str,
        params: Optional[dict[str, Any]] = None,
        max_pages: int = 5,
    ) -> list[Any]:
        """Paginates across GitHub collection endpoints (e.g. repos, commits)."""
        all_items: list[Any] = []
        p = dict(params or {})
        p["per_page"] = p.get("per_page", 100)
        p["page"] = 1

        for _ in range(max_pages):
            page_data = await self.get(endpoint, params=p)
            if not isinstance(page_data, list):
                if isinstance(page_data, dict) and "items" in page_data:
                    page_data = page_data["items"]
                else:
                    all_items.append(page_data)
                    break

            if not page_data:
                break
            all_items.extend(page_data)
            if len(page_data) < p["per_page"]:
                break
            p["page"] += 1

        return all_items
