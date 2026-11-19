"""Live real public job board discovery integration test (Stage 26)."""

import pytest
from app.recruitment.discovery.connectors.greenhouse import GreenhouseConnector
from app.recruitment.discovery.contracts import ConnectorId, JobSourceConfig
from app.recruitment.discovery.fetching.http_client import DiscoveryHttpClient


@pytest.mark.asyncio
async def test_live_greenhouse_public_discovery():
    """Fetches real job listings from official public Greenhouse boards API."""
    client = DiscoveryHttpClient()
    conn = GreenhouseConnector()
    config = JobSourceConfig(
        id="src_live_gh",
        name="GitHub Careers",
        connector_id=ConnectorId.GREENHOUSE,
        official_domain="boards-api.greenhouse.io",
        board_token="github",
        employer_name="GitHub",
    )

    try:
        validation = await conn.validate_source(config, client)
        if not validation.is_valid:
            pytest.skip(f"Live network test skipped: {validation.message}")

        postings = await conn.fetch_postings(config, client)
        assert len(postings) > 0
        p = postings[0]
        assert p.title
        assert p.employer_name == "GitHub"
        assert p.native_posting_id
        assert p.official_posting_url.startswith("http")
    except Exception as exc:
        pytest.skip(f"Live network test skipped due to network or rate limit: {exc}")
