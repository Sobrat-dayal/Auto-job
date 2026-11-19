"""Unit tests for Job Discovery Engine data contracts and models (Stage 26)."""

import pytest
from app.recruitment.discovery.contracts import (
    ConnectorCapability,
    ConnectorId,
    ConnectorManifest,
    DiscoverySettingsConfig,
    DiscoveryTaskCreateRequest,
    DiscoveryTaskRecord,
    DiscoveryTaskState,
    ExtractionConfidence,
    ExtractedCompensation,
    ExtractedLocation,
    ExtractedPosting,
    FieldProvenance,
    JobSourceConfig,
    JobSourceHealth,
    JobSourceObservation,
    JobSourceSnapshot,
    PostingAvailability,
    PrefilterOutcome,
    SnapshotCompleteness,
    SourceAccessStatus,
    SourceCategory,
)


def test_connector_manifest_defaults():
    manifest = ConnectorManifest(
        connector_id=ConnectorId.GREENHOUSE,
        provider_name="Greenhouse Job Board",
        endpoint_category=SourceCategory.EMPLOYER_ATS_BOARD,
        supported_capabilities=[
            ConnectorCapability.LIST_POSTINGS,
            ConnectorCapability.GET_POSTING_DETAILS,
        ],
        last_verified_doc_url="https://developers.greenhouse.io/job-board.html",
    )
    assert manifest.connector_id == ConnectorId.GREENHOUSE
    assert manifest.version == "1.0.0"
    assert manifest.authentication_method == "none"
    assert ConnectorCapability.LIST_POSTINGS in manifest.supported_capabilities


def test_job_source_config_defaults():
    config = JobSourceConfig(
        name="Stripe Careers",
        connector_id=ConnectorId.GREENHOUSE,
        official_domain="boards-api.greenhouse.io",
        board_token="stripe",
    )
    assert config.id.startswith("src_")
    assert config.is_enabled is True
    assert config.rate_limit_rpm == 30
    assert config.access_status == SourceAccessStatus.UNVERIFIED


def test_extracted_posting_provenance():
    prov = FieldProvenance(
        source_id="src_1",
        retrieved_at="2026-03-30T10:00:00Z",
        raw_field_path="job.title",
        parser_method="json_parser",
        confidence=ExtractionConfidence.HIGH,
    )
    posting = ExtractedPosting(
        native_posting_id="12345",
        title="Software Engineer",
        employer_name="Stripe",
        official_posting_url="https://boards.greenhouse.io/stripe/jobs/12345",
        provenance={"title": prov},
    )
    assert posting.title == "Software Engineer"
    assert posting.provenance["title"].confidence == ExtractionConfidence.HIGH


def test_job_source_observation():
    obs = JobSourceObservation(
        source_id="src_1",
        provider=ConnectorId.GREENHOUSE,
        native_posting_id="12345",
        source_url="https://boards.greenhouse.io/stripe/jobs/12345",
        title="Staff Engineer",
        employer="Stripe",
        availability=PostingAvailability.AVAILABLE,
        prefilter_status=PrefilterOutcome.PREFILTER_ACCEPTED,
    )
    assert obs.id.startswith("obs_")
    assert obs.availability == PostingAvailability.AVAILABLE
    assert obs.prefilter_status == PrefilterOutcome.PREFILTER_ACCEPTED


def test_snapshot_completeness_enums():
    assert SnapshotCompleteness.COMPLETE == "complete"
    assert SnapshotCompleteness.PARTIAL == "partial"
    assert SnapshotCompleteness.RATE_LIMITED == "rate_limited"
    assert SnapshotCompleteness.FAILED == "failed"
