"""Safe, rate-limited, conditional HTTP client for job discovery (Stage 26)."""

import asyncio
from datetime import UTC, datetime
import logging
import random
import time
from typing import Any, Optional
import httpx

from app.recruitment.discovery.errors import (
    RateLimitExceededError,
    SSRFSecurityError,
)
from app.recruitment.discovery.fetching.caching import http_cache_manager
from app.recruitment.discovery.security.url_validation import assert_safe_url

logger = logging.getLogger("autonom.recruitment.discovery.fetching.http_client")


class DiscoveryHttpResponse:
    def __init__(
        self,
        status_code: int,
        headers: dict[str, str],
        text: str,
        latency_ms: float,
        is_cached_304: bool = False,
    ) -> None:
        self.status_code = status_code
        self.headers = headers
        self.text = text
        self.latency_ms = latency_ms
        self.is_cached_304 = is_cached_304

    def json(self) -> Any:
        import json
        return json.loads(self.text)


class DiscoveryHttpClient:
    """Manages rate-limited, SSRF-checked, conditional HTTP requests for job source discovery."""

    def __init__(self, timeout_seconds: float = 20.0) -> None:
        self.timeout_seconds = timeout_seconds
        self._source_request_timestamps: dict[str, list[float]] = {}
        self._rate_limit_cooldowns: dict[str, float] = {}

    async def _enforce_rate_limit(self, source_id: str, rate_limit_rpm: int) -> None:
        """Enforce request rate limit using sliding window."""
        now = time.time()

        # Check active cooldown from previous HTTP 429
        cooldown_until = self._rate_limit_cooldowns.get(source_id, 0.0)
        if now < cooldown_until:
            wait_time = cooldown_until - now
            raise RateLimitExceededError(source_id, retry_after_seconds=int(wait_time))

        if rate_limit_rpm <= 0:
            return

        window_start = now - 60.0
        timestamps = self._source_request_timestamps.get(source_id, [])
        # Prune older than 60s
        timestamps = [t for t in timestamps if t > window_start]
        self._source_request_timestamps[source_id] = timestamps

        if len(timestamps) >= rate_limit_rpm:
            # Need to pause
            oldest = timestamps[0]
            sleep_needed = (oldest + 60.0) - now + random.uniform(0.1, 0.5)
            if sleep_needed > 0:
                logger.info(f"Throttling source '{source_id}' for {sleep_needed:.2f}s to respect RPM {rate_limit_rpm}")
                await asyncio.sleep(min(sleep_needed, 5.0))

        self._source_request_timestamps.setdefault(source_id, []).append(time.time())

    async def fetch(
        self,
        url: str,
        source_id: str = "default_source",
        rate_limit_rpm: int = 30,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        use_cache: bool = True,
        enforce_ssrf: bool = True,
        max_retries: int = 2,
    ) -> DiscoveryHttpResponse:
        """Fetch URL with SSRF checks, rate-limit governance, conditional headers, and safe retries."""
        # 1. SSRF Safety Verification
        assert_safe_url(url, enforce_ssrf=enforce_ssrf)

        # 2. Rate Limit Enforcement
        await self._enforce_rate_limit(source_id, rate_limit_rpm)

        req_headers = {
            "User-Agent": "AUTONOM-Recruitment-Discovery/1.0 (Desktop; Windows; Read-Only)",
            "Accept": "application/json, text/html, application/xml, text/plain;q=0.9, */*;q=0.8",
        }
        if headers:
            req_headers.update(headers)

        if use_cache:
            cond_headers = http_cache_manager.get_conditional_headers(url)
            req_headers.update(cond_headers)

        attempt = 0
        last_error: Optional[Exception] = None

        while attempt <= max_retries:
            attempt += 1
            start_time = time.perf_counter()
            try:
                async with httpx.AsyncClient(
                    timeout=httpx.Timeout(self.timeout_seconds),
                    follow_redirects=False,  # Handle redirects manually to re-verify SSRF
                ) as client:
                    current_url = url
                    current_params = params
                    redirect_count = 0
                    max_redirects = 5

                    while redirect_count <= max_redirects:
                        # Re-verify SSRF on every hop
                        assert_safe_url(current_url, enforce_ssrf=enforce_ssrf)

                        resp = await client.get(current_url, headers=req_headers, params=current_params)
                        current_params = None  # Params applied only on first request

                        if resp.is_redirect:
                            redirect_count += 1
                            redirect_url = resp.headers.get("Location")
                            if not redirect_url:
                                break
                            current_url = redirect_url
                            continue
                        break

                    latency_ms = (time.perf_counter() - start_time) * 1000.0

                    # 3. Handle HTTP 304 Not Modified
                    if resp.status_code == 304:
                        cached_body = http_cache_manager.get_cached_body(url) or ""
                        return DiscoveryHttpResponse(
                            status_code=304,
                            headers=dict(resp.headers),
                            text=cached_body,
                            latency_ms=latency_ms,
                            is_cached_304=True,
                        )

                    # 4. Handle HTTP 429 Too Many Requests
                    if resp.status_code == 429:
                        retry_after = resp.headers.get("Retry-After")
                        cooldown_secs = int(retry_after) if (retry_after and retry_after.isdigit()) else 60
                        self._rate_limit_cooldowns[source_id] = time.time() + cooldown_secs
                        raise RateLimitExceededError(source_id, retry_after_seconds=cooldown_secs)

                    # Record for conditional caching
                    if resp.status_code == 200:
                        http_cache_manager.record_response(
                            url=url,
                            status_code=resp.status_code,
                            headers=dict(resp.headers),
                            body=resp.text,
                        )

                    return DiscoveryHttpResponse(
                        status_code=resp.status_code,
                        headers=dict(resp.headers),
                        text=resp.text,
                        latency_ms=latency_ms,
                    )

            except (httpx.ConnectTimeout, httpx.ReadTimeout, httpx.ConnectError) as exc:
                last_error = exc
                if attempt <= max_retries:
                    # Exponential backoff + jitter
                    backoff = (2 ** attempt) * 0.5 + random.uniform(0.1, 0.4)
                    await asyncio.sleep(backoff)
                else:
                    raise exc

        raise last_error or RuntimeError("HTTP request failed after maximum retries")

    async def get(
        self,
        url: str,
        source_id: str = "default_source",
        rate_limit_rpm: int = 30,
        headers: Optional[dict[str, str]] = None,
        params: Optional[dict[str, Any]] = None,
        use_cache: bool = True,
        enforce_ssrf: bool = True,
        max_retries: int = 2,
    ) -> DiscoveryHttpResponse:
        """Alias for fetch."""
        return await self.fetch(
            url=url,
            source_id=source_id,
            rate_limit_rpm=rate_limit_rpm,
            headers=headers,
            params=params,
            use_cache=use_cache,
            enforce_ssrf=enforce_ssrf,
            max_retries=max_retries,
        )
