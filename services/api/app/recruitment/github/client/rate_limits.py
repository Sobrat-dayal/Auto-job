"""GitHub API Rate-Limit Controller and Throttling Engine (Stage 22)."""

from __future__ import annotations

import logging
import time
from typing import Optional

from app.recruitment.github.errors import GitHubRateLimitExceededError

logger = logging.getLogger("autonom.recruitment.github.rate_limits")


class RateLimitController:
    """Monitors GitHub API rate limits, enforces backoff, and tracks reset windows."""

    def __init__(self) -> None:
        self._limit: int = 60
        self._remaining: int = 60
        self._reset_timestamp: int = int(time.time()) + 3600
        self._is_rate_limited: bool = False

    def update_from_headers(self, headers: dict[str, str]) -> None:
        """Parses standard GitHub rate limit headers from HTTP response."""
        norm_headers = {k.lower(): v for k, v in headers.items()}
        if "x-ratelimit-limit" in norm_headers:
            try:
                self._limit = int(norm_headers["x-ratelimit-limit"])
            except ValueError:
                pass
        if "x-ratelimit-remaining" in norm_headers:
            try:
                self._remaining = int(norm_headers["x-ratelimit-remaining"])
                if self._remaining <= 1:
                    self._is_rate_limited = True
                else:
                    self._is_rate_limited = False
            except ValueError:
                pass
        if "x-ratelimit-reset" in norm_headers:
            try:
                self._reset_timestamp = int(norm_headers["x-ratelimit-reset"])
            except ValueError:
                pass

    def check_preflight(self) -> None:
        """Checks if requests are currently blocked due to active rate-limiting."""
        now = int(time.time())
        if self._is_rate_limited and now < self._reset_timestamp:
            wait_sec = self._reset_timestamp - now
            logger.warning(f"GitHub API rate limit active. Remaining: {self._remaining}. Wait: {wait_sec}s")
            raise GitHubRateLimitExceededError(
                f"GitHub API rate limit reached. Reset in {wait_sec} seconds.",
                reset_timestamp=self._reset_timestamp,
            )
        elif self._is_rate_limited and now >= self._reset_timestamp:
            # Window expired; reset flag
            self._is_rate_limited = False
            self._remaining = self._limit

    @property
    def limit(self) -> int:
        return self._limit

    @property
    def remaining(self) -> int:
        return self._remaining

    @property
    def reset_timestamp(self) -> int:
        return self._reset_timestamp

    @property
    def is_rate_limited(self) -> bool:
        return self._is_rate_limited and int(time.time()) < self._reset_timestamp
