"""Unit tests for GitHub REST client, rate limit controller, and ETag caching."""

import pytest
from app.recruitment.github.client.caching import ETagCacheManager
from app.recruitment.github.client.rate_limits import RateLimitController
from app.recruitment.github.client.rest import GitHubRestClient, redact_token_string
from app.recruitment.github.errors import (
    GitHubAuthenticationError,
    GitHubNotFoundError,
    GitHubPermissionDeniedError,
    GitHubRateLimitExceededError,
)


def test_rate_limit_controller_tracking():
    rl = RateLimitController()
    assert rl.remaining == 60
    assert rl.is_rate_limited is False

    # Simulate headers update
    rl.update_from_headers({
        "x-ratelimit-limit": "5000",
        "x-ratelimit-remaining": "42",
        "x-ratelimit-reset": "1770000000",
    })
    assert rl.remaining == 42
    assert rl.limit == 5000
    assert rl.reset_timestamp == 1770000000

    # Exhaust rate limit
    rl.update_from_headers({
        "x-ratelimit-remaining": "0",
        "x-ratelimit-reset": "1999999999",
    })
    assert rl.is_rate_limited is True

    # Assert exception raised when preflight check runs
    with pytest.raises(GitHubRateLimitExceededError):
        rl.check_preflight()


def test_etag_cache_manager():
    cache = ETagCacheManager()
    assert cache.entry_count == 0

    cache.set("/repos/octocat/hello-world", '"etag_12345"', {"name": "hello-world"})
    assert cache.entry_count == 1

    etag = cache.get_etag("/repos/octocat/hello-world")
    data = cache.get_data("/repos/octocat/hello-world")
    assert etag == '"etag_12345"'
    assert data["name"] == "hello-world"

    # Cache invalidation
    cache.invalidate("/repos/octocat/hello-world")
    assert cache.get_etag("/repos/octocat/hello-world") is None
    assert cache.entry_count == 0


def test_token_redaction_utility():
    raw_text = "Authorization: Bearer ghp_123456789012345678901234567890123456 in request"
    redacted = redact_token_string(raw_text)
    assert "ghp_1234567890" not in redacted
    assert "[REDACTED_GITHUB_TOKEN]" in redacted


def test_github_rest_client_init_and_headers():
    client = GitHubRestClient(access_token="ghp_dummytoken999999999999999999999999")
    headers = client._get_headers()
    assert headers["X-GitHub-Api-Version"] == "2022-11-28"
    assert headers["Accept"] == "application/vnd.github+json"
    assert "Bearer" in headers["Authorization"]
    assert client.access_token is not None

    client_anon = GitHubRestClient(access_token=None)
    headers_anon = client_anon._get_headers()
    assert "Authorization" not in headers_anon
    assert client_anon.access_token is None
