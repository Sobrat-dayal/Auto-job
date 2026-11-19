"""Unit tests for Discovery Synchronization and Snapshot Safety Invariant (Stage 26).

CRITICAL INVARIANT TEST: Verifies that partial snapshots NEVER mass-close postings!
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from app.recruitment.discovery.connectors.registry import connector_registry
from app.recruitment.discovery.contracts import (
    ConnectorId,
    ExtractedLocation,
    ExtractedPosting,
    JobSourceConfig,
    PostingAvailability,
    SnapshotCompleteness,
    SourceAccessStatus,
)
from app.recruitment.discovery.sources.registry import source_registry
from app.recruitment.discovery.synchronization.coordinator import DiscoveryCoordinator


@pytest.fixture
def mock_client():
    client = MagicMock()
    client.get = AsyncMock()
    return client


@pytest.mark.asyncio
async def test_initial_sync_and_change_detection(mock_client):
    coordinator = DiscoveryCoordinator(http_client=mock_client)

    # Setup source
    src = JobSourceConfig(
        id="src_test_sync",
        name="Test Corp",
        connector_id=ConnectorId.GREENHOUSE,
        official_domain="boards-api.greenhouse.io",
        board_token="testcorp",
        employer_name="Test Corp",
        access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
    )
    source_registry._sources[src.id] = src

    # Mock connector
    connector = connector_registry.get_connector(ConnectorId.GREENHOUSE)
    posting_v1 = ExtractedPosting(
        native_posting_id="post_1",
        title="Software Engineer I",
        employer_name="Test Corp",
        official_posting_url="https://boards.greenhouse.io/testcorp/jobs/1",
        description_text="Initial description",
    )
    connector.fetch_postings = AsyncMock(return_value=[posting_v1])

    # First complete sync
    snap1 = await coordinator.sync_source(src.id)
    assert snap1.completeness == SnapshotCompleteness.COMPLETE
    assert snap1.new_count == 1
    assert snap1.updated_count == 0
    assert snap1.closed_count == 0

    obs = coordinator.find_observation_by_native_id(src.id, "post_1")
    assert obs is not None
    assert obs.title == "Software Engineer I"
    assert obs.availability == PostingAvailability.AVAILABLE

    # Second sync: title updated
    posting_v2 = ExtractedPosting(
        native_posting_id="post_1",
        title="Software Engineer II",
        employer_name="Test Corp",
        official_posting_url="https://boards.greenhouse.io/testcorp/jobs/1",
        description_text="Updated description",
    )
    connector.fetch_postings = AsyncMock(return_value=[posting_v2])

    snap2 = await coordinator.sync_source(src.id)
    assert snap2.completeness == SnapshotCompleteness.COMPLETE
    assert snap2.new_count == 0
    assert snap2.updated_count == 1
    assert snap2.closed_count == 0

    obs_updated = coordinator.find_observation_by_native_id(src.id, "post_1")
    assert obs_updated.title == "Software Engineer II"


@pytest.mark.asyncio
async def test_partial_snapshot_never_closes_postings(mock_client):
    """CRITICAL SAFETY INVARIANT TEST:
    When a fetch fails partially or is interrupted/rate-limited, missing postings
    must NEVER be marked as closed!
    """
    coordinator = DiscoveryCoordinator(http_client=mock_client)

    src = JobSourceConfig(
        id="src_safety_test",
        name="Safety Corp",
        connector_id=ConnectorId.GREENHOUSE,
        official_domain="boards-api.greenhouse.io",
        board_token="safetycorp",
        employer_name="Safety Corp",
        access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
    )
    source_registry._sources[src.id] = src

    connector = connector_registry.get_connector(ConnectorId.GREENHOUSE)
    posting_1 = ExtractedPosting(
        native_posting_id="job_active_1",
        title="Senior Security Architect",
        employer_name="Safety Corp",
        official_posting_url="https://boards.greenhouse.io/safetycorp/jobs/1",
    )
    posting_2 = ExtractedPosting(
        native_posting_id="job_active_2",
        title="Staff Infrastructure Engineer",
        employer_name="Safety Corp",
        official_posting_url="https://boards.greenhouse.io/safetycorp/jobs/2",
    )

    # Initial sync observes 2 active jobs
    connector.fetch_postings = AsyncMock(return_value=[posting_1, posting_2])
    snap1 = await coordinator.sync_source(src.id)
    assert snap1.completeness == SnapshotCompleteness.COMPLETE
    assert snap1.new_count == 2

    obs1 = coordinator.find_observation_by_native_id(src.id, "job_active_1")
    obs2 = coordinator.find_observation_by_native_id(src.id, "job_active_2")
    assert obs1.availability == PostingAvailability.AVAILABLE
    assert obs2.availability == PostingAvailability.AVAILABLE

    # SIMULATE PARTIAL FAILURE: Connector raises an error or rate limit during fetch
    connector.fetch_postings = AsyncMock(side_effect=Exception("HTTP 429: Rate limited by provider API"))

    snap_failed = await coordinator.sync_source(src.id)
    assert snap_failed.completeness in (SnapshotCompleteness.PARTIAL, SnapshotCompleteness.RATE_LIMITED)
    assert snap_failed.closed_count == 0  # MUST BE ZERO!

    # Verify both postings are STILL AVAILABLE, NOT CLOSED!
    obs1_after = coordinator.find_observation_by_native_id(src.id, "job_active_1")
    obs2_after = coordinator.find_observation_by_native_id(src.id, "job_active_2")
    assert obs1_after.availability == PostingAvailability.AVAILABLE
    assert obs2_after.availability == PostingAvailability.AVAILABLE


@pytest.mark.asyncio
async def test_complete_snapshot_closes_removed_postings(mock_client):
    """When a snapshot is verified COMPLETE, absent postings are properly marked CLOSED."""
    coordinator = DiscoveryCoordinator(http_client=mock_client)

    src = JobSourceConfig(
        id="src_closing_test",
        name="Closing Corp",
        connector_id=ConnectorId.GREENHOUSE,
        official_domain="boards-api.greenhouse.io",
        board_token="closingcorp",
        employer_name="Closing Corp",
        access_status=SourceAccessStatus.AVAILABLE_PUBLIC,
    )
    source_registry._sources[src.id] = src

    connector = connector_registry.get_connector(ConnectorId.GREENHOUSE)
    posting_1 = ExtractedPosting(
        native_posting_id="closing_1",
        title="Frontend Developer",
        employer_name="Closing Corp",
        official_posting_url="https://boards.greenhouse.io/closingcorp/jobs/1",
    )
    posting_2 = ExtractedPosting(
        native_posting_id="closing_2",
        title="Backend Developer",
        employer_name="Closing Corp",
        official_posting_url="https://boards.greenhouse.io/closingcorp/jobs/2",
    )

    # Initial sync has both
    connector.fetch_postings = AsyncMock(return_value=[posting_1, posting_2])
    await coordinator.sync_source(src.id)

    # Next complete sync only returns posting_1 (posting_2 removed by employer)
    connector.fetch_postings = AsyncMock(return_value=[posting_1])
    snap = await coordinator.sync_source(src.id)

    assert snap.completeness == SnapshotCompleteness.COMPLETE
    assert snap.closed_count == 1

    obs2 = coordinator.find_observation_by_native_id(src.id, "closing_2")
    assert obs2.availability == PostingAvailability.CLOSED
