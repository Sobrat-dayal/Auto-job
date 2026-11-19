"""Unit tests for Job Source Connectors with fixtures (Stage 26)."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.recruitment.discovery.connectors.ashby import AshbyConnector
from app.recruitment.discovery.connectors.career_page import CareerPageConnector
from app.recruitment.discovery.connectors.greenhouse import GreenhouseConnector
from app.recruitment.discovery.connectors.json_feed import JsonFeedConnector
from app.recruitment.discovery.connectors.lever import LeverConnector
from app.recruitment.discovery.connectors.manual_import import ManualImportConnector
from app.recruitment.discovery.connectors.rss_atom import RssAtomConnector
from app.recruitment.discovery.connectors.url_import import UrlImportConnector
from app.recruitment.discovery.connectors.usajobs import USAJobsConnector
from app.recruitment.discovery.contracts import (
    ConnectorId,
    JobSourceConfig,
    ManualImportRequest,
    SourceAccessStatus,
    UrlImportRequest,
)


@pytest.fixture
def mock_http_client():
    client = MagicMock()
    client.fetch = AsyncMock()
    client.get = client.fetch
    return client


@pytest.mark.asyncio
async def test_greenhouse_connector_parsing(mock_http_client):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "jobs": [
            {
                "id": 998877,
                "title": "Backend Systems Engineer",
                "absolute_url": "https://boards.greenhouse.io/stripe/jobs/998877",
                "location": {"name": "San Francisco, CA (Remote)"},
                "departments": [{"name": "Engineering"}],
                "offices": [{"name": "San Francisco"}],
                "updated_at": "2026-03-20T12:00:00Z",
                "content": "<p>Build high-throughput distributed systems in Go/Python. Salary range $160,000 - $210,000 per year.</p>",
            }
        ]
    }
    mock_http_client.get.return_value = mock_resp

    conn = GreenhouseConnector()
    config = JobSourceConfig(
        id="src_stripe",
        name="Stripe",
        connector_id=ConnectorId.GREENHOUSE,
        official_domain="boards-api.greenhouse.io",
        board_token="stripe",
        employer_name="Stripe",
    )

    postings = await conn.fetch_postings(config, mock_http_client)
    assert len(postings) == 1
    p = postings[0]
    assert p.native_posting_id == "998877"
    assert p.title == "Backend Systems Engineer"
    assert p.employer_name == "Stripe"
    assert p.location.city == "San Francisco"
    assert p.location.is_remote is True
    assert p.department == "Engineering"
    assert p.compensation is not None
    assert p.compensation.min_amount == 160000.0
    assert p.compensation.max_amount == 210000.0


@pytest.mark.asyncio
async def test_lever_connector_parsing(mock_http_client):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = [
        {
            "id": "lever_abc_123",
            "text": "Senior Platform Engineer",
            "hostedUrl": "https://jobs.lever.co/netflix/lever_abc_123",
            "applyUrl": "https://jobs.lever.co/netflix/lever_abc_123/apply",
            "categories": {
                "team": "Core Engineering",
                "location": "Los Gatos, CA",
                "commitment": "Full-Time",
            },
            "workplaceType": "hybrid",
            "descriptionPlain": "Design cloud architecture. Base pay $180,000 to $240,000 annually.",
            "createdAt": 1742472000000,
        }
    ]
    mock_http_client.get.return_value = mock_resp

    conn = LeverConnector()
    config = JobSourceConfig(
        id="src_netflix",
        name="Netflix",
        connector_id=ConnectorId.LEVER,
        official_domain="api.lever.co",
        site_id="netflix",
        employer_name="Netflix",
    )

    postings = await conn.fetch_postings(config, mock_http_client)
    assert len(postings) == 1
    p = postings[0]
    assert p.native_posting_id == "lever_abc_123"
    assert p.title == "Senior Platform Engineer"
    assert p.location.workplace_type == "hybrid"
    assert p.compensation is not None
    assert p.compensation.min_amount == 180000.0
    assert p.compensation.max_amount == 240000.0


@pytest.mark.asyncio
async def test_ashby_connector_parsing(mock_http_client):
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "jobs": [
            {
                "id": "ashby_open_01",
                "title": "Research Engineer, Post-Training",
                "jobUrl": "https://jobs.ashbyhq.com/openai/ashby_open_01",
                "applyUrl": "https://jobs.ashbyhq.com/openai/ashby_open_01/application",
                "department": "Safety",
                "location": "San Francisco, California, United States",
                "isRemote": False,
                "employmentType": "FullTime",
                "publishedAt": "2026-03-25T14:30:00Z",
                "descriptionHtml": "<p>Advance multimodal foundation models.</p>",
                "compensation": {
                    "compensationTierSummary": "$245,000—$320,000 USD",
                },
            }
        ]
    }
    mock_http_client.get.return_value = mock_resp

    conn = AshbyConnector()
    config = JobSourceConfig(
        id="src_openai",
        name="OpenAI",
        connector_id=ConnectorId.ASHBY,
        official_domain="api.ashbyhq.com",
        board_token="openai",
        employer_name="OpenAI",
    )

    postings = await conn.fetch_postings(config, mock_http_client)
    assert len(postings) == 1
    p = postings[0]
    assert p.native_posting_id == "ashby_open_01"
    assert p.title == "Research Engineer, Post-Training"
    assert p.compensation is not None
    assert p.compensation.min_amount == 245000.0
    assert p.compensation.max_amount == 320000.0


@pytest.mark.asyncio
async def test_usajobs_connector_credentials_handling(mock_http_client):
    conn = USAJobsConnector()
    config_unauthorized = JobSourceConfig(
        id="src_usajobs",
        name="USAJOBS",
        connector_id=ConnectorId.USAJOBS,
        official_domain="data.usajobs.gov",
    )

    # Validation should indicate credentials required if none configured
    val = await conn.validate_source(config_unauthorized, mock_http_client)
    assert val.access_status == SourceAccessStatus.REQUIRES_CREDENTIALS


@pytest.mark.asyncio
async def test_rss_atom_connector_parsing(mock_http_client):
    rss_xml = """<?xml version="1.0" encoding="UTF-8"?>
    <rss version="2.0">
        <channel>
            <title>Tech Jobs Feed</title>
            <item>
                <guid>rss_job_101</guid>
                <title>Lead Cloud Architect</title>
                <link>https://example.com/jobs/101</link>
                <description>&lt;p&gt;Looking for an AWS/GCP architect. Remote. Salary $150k - $200k.&lt;/p&gt;</description>
                <pubDate>Mon, 23 Mar 2026 12:00:00 GMT</pubDate>
            </item>
        </channel>
    </rss>
    """
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = rss_xml
    mock_http_client.get.return_value = mock_resp

    conn = RssAtomConnector()
    config = JobSourceConfig(
        id="src_rss",
        name="Tech Feed",
        connector_id=ConnectorId.RSS_ATOM,
        official_domain="example.com",
        feed_url="https://example.com/rss",
        employer_name="Tech Corp",
    )

    postings = await conn.fetch_postings(config, mock_http_client)
    assert len(postings) == 1
    p = postings[0]
    assert p.native_posting_id == "rss_job_101"
    assert p.title == "Lead Cloud Architect"
    assert p.official_posting_url == "https://example.com/jobs/101"


def test_manual_import_connector():
    conn = ManualImportConnector()
    req = ManualImportRequest(
        title="Principal AI Architect",
        employer_name="Anthropic",
        location="Remote, US",
        work_arrangement="remote",
        compensation_text="$250,000 - $350,000 per year",
        description="Lead agentic AI system architecture.",
    )
    posting = conn.create_from_request(req)
    assert posting.title == "Principal AI Architect"
    assert posting.employer_name == "Anthropic"
    assert posting.location.is_remote is True
    assert posting.compensation is not None
    assert posting.compensation.min_amount == 250000.0
