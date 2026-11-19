"""Conditional request metadata and caching for job discovery (Stage 26)."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Optional


@dataclass
class HttpCacheEntry:
    url: str
    etag: Optional[str] = None
    last_modified: Optional[str] = None
    stored_at: str = ""
    status_code: int = 200
    body: str = ""


class HttpCacheManager:
    """Manages conditional HTTP request validators (ETags, Last-Modified) to prevent redundant payload transfers."""

    def __init__(self) -> None:
        self._entries: dict[str, HttpCacheEntry] = {}

    def get_conditional_headers(self, url: str) -> dict[str, str]:
        """Return If-None-Match or If-Modified-Since headers if cached validator exists."""
        entry = self._entries.get(url)
        if not entry:
            return {}

        headers = {}
        if entry.etag:
            headers["If-None-Match"] = entry.etag
        if entry.last_modified:
            headers["If-Modified-Since"] = entry.last_modified

        return headers

    def record_response(
        self,
        url: str,
        status_code: int,
        headers: dict[str, str],
        body: str = "",
    ) -> None:
        """Store ETag / Last-Modified from response headers."""
        etag = headers.get("etag") or headers.get("ETag")
        last_modified = headers.get("last-modified") or headers.get("Last-Modified")

        if etag or last_modified:
            self._entries[url] = HttpCacheEntry(
                url=url,
                etag=etag,
                last_modified=last_modified,
                stored_at=datetime.now(UTC).isoformat(),
                status_code=status_code,
                body=body,
            )

    def get_cached_body(self, url: str) -> Optional[str]:
        """Return cached response body if available."""
        entry = self._entries.get(url)
        return entry.body if entry else None

    def clear(self) -> None:
        self._entries.clear()


http_cache_manager = HttpCacheManager()
