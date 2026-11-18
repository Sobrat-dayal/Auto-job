"""ETag and Conditional Request Cache Manager for GitHub API (Stage 22)."""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger("autonom.recruitment.github.cache")


class ETagCacheManager:
    """Stores ETags and cached payloads to enable HTTP 304 Not Modified requests."""

    def __init__(self) -> None:
        self._cache: dict[str, tuple[str, Any]] = {}  # endpoint -> (etag, data)

    def get_etag(self, endpoint: str) -> Optional[str]:
        entry = self._cache.get(endpoint)
        return entry[0] if entry else None

    def get_data(self, endpoint: str) -> Optional[Any]:
        entry = self._cache.get(endpoint)
        return entry[1] if entry else None

    def set(self, endpoint: str, etag: str, data: Any) -> None:
        self._cache[endpoint] = (etag, data)

    def invalidate(self, prefix: Optional[str] = None) -> int:
        """Invalidates entries matching prefix, or all entries if prefix is None."""
        if not prefix:
            count = len(self._cache)
            self._cache.clear()
            return count
        keys_to_del = [k for k in self._cache if k.startswith(prefix)]
        for k in keys_to_del:
            del self._cache[k]
        return len(keys_to_del)

    @property
    def entry_count(self) -> int:
        return len(self._cache)
