"""Canonical contracts, enums, and data models for Multi-Source Job Discovery Engine (Stage 26)."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class ConnectorId(StrEnum):
    GREENHOUSE = "greenhouse"
    LEVER = "lever"
    ASHBY = "ashby"
    USAJOBS = "usajobs"
    RSS_ATOM = "rss_atom"
    JSON_FEED = "json_feed"
    CAREER_PAGE = "career_page"
    MANUAL_IMPORT = "manual_import"
    URL_IMPORT = "url_import"


class SourceCategory(StrEnum):
    OFFICIAL_PUBLIC_API = "official_public_api"
    AUTHORIZED_PARTNER_API = "authorized_partner_api"
    EMPLOYER_ATS_BOARD = "employer_ats_board"
    EMPLOYER_CAREER_SITE = "employer_career_site"
    RSS_ATOM_FEED = "rss_atom_feed"
    STRUCTURED_JSON_FEED = "structured_json_feed"
    USER_SUPPLIED_URL = "user_supplied_url"
    MANUAL_IMPORTED = "manual_imported"
    RESTRICTED_COMMERCIAL = "restricted_commercial"


class SourceAccessStatus(StrEnum):
    AVAILABLE_PUBLIC = "available_public"
    AVAILABLE_AUTHORIZED = "available_authorized"
    REQUIRES_CREDENTIALS = "requires_credentials"
    REQUIRES_PARTNER_ACCESS = "requires_partner_access"
    MANUAL_IMPORT_ONLY = "manual_import_only"
    TEMPORARILY_RATE_LIMITED = "temporarily_rate_limited"
    ACCESS_DENIED = "access_denied"
    RESTRICTED_BY_TERMS = "restricted_by_terms"
    UNAVAILABLE = "unavailable"
    UNVERIFIED = "unverified"


class PostingAvailability(StrEnum):
    AVAILABLE = "available"
    CLOSED = "closed"
    EXPIRED = "expired"
    REMOVED = "removed"
    REDIRECTED = "redirected"
    UNKNOWN = "unknown"
    SOURCE_UNAVAILABLE = "source_unavailable"


class SnapshotCompleteness(StrEnum):
    COMPLETE = "complete"
    PARTIAL = "partial"
    INTERRUPTED = "interrupted"
    RATE_LIMITED = "rate_limited"
    INVALID = "invalid"
    FAILED = "failed"


class DiscoveryTaskState(StrEnum):
    CREATED = "created"
    VALIDATING = "validating"
    QUEUED = "queued"
    RUNNING = "running"
    PAUSED = "paused"
    RATE_LIMITED = "rate_limited"
    PARTIALLY_COMPLETED = "partially_completed"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class PrefilterOutcome(StrEnum):
    PREFILTER_ACCEPTED = "prefilter_accepted"
    PREFILTER_REJECTED = "prefilter_rejected"
    NEEDS_REVIEW = "needs_review"
    UNKNOWN = "unknown"


class ExtractionConfidence(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNKNOWN = "unknown"


class ConnectorCapability(StrEnum):
    LIST_POSTINGS = "list_postings"
    GET_POSTING_DETAILS = "get_posting_details"
    SERVER_SEARCH = "server_search"
    SERVER_FILTER = "server_filter"
    PAGINATION = "pagination"
    CONDITIONAL_FETCH = "conditional_fetch"
    CREDENTIAL_GATED = "credential_gated"
    STRUCTURED_SCHEMA_ORG = "structured_schema_org"
    BROWSER_RENDER_FALLBACK = "browser_render_fallback"


# =============================================================================
# Connector & Manifest Models
# =============================================================================

class ConnectorManifest(BaseModel):
    connector_id: ConnectorId
    version: str = "1.0.0"
    provider_name: str
    endpoint_category: SourceCategory
    authentication_method: str = "none"  # none, api_key, bearer_token, custom_headers
    required_permissions: list[str] = Field(default_factory=list)
    supported_capabilities: list[ConnectorCapability] = Field(default_factory=list)
    provider_restrictions: list[str] = Field(default_factory=list)
    last_verified_doc_url: str
    last_verified_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# =============================================================================
# Source Configuration & Health Models
# =============================================================================

class JobSourceConfig(BaseModel):
    id: str = Field(default_factory=lambda: f"src_{uuid4().hex[:8]}")
    name: str
    connector_id: ConnectorId
    category: SourceCategory = SourceCategory.EMPLOYER_ATS_BOARD
    official_domain: str
    board_token: Optional[str] = None
    site_id: Optional[str] = None
    feed_url: Optional[str] = None
    employer_name: Optional[str] = None
    access_status: SourceAccessStatus = SourceAccessStatus.UNVERIFIED
    is_enabled: bool = True
    rate_limit_rpm: int = 30
    custom_headers: dict[str, str] = Field(default_factory=dict)
    custom_params: dict[str, Any] = Field(default_factory=dict)
    credential_alias: Optional[str] = None
    last_synced_at: Optional[str] = None
    error_status: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class JobSourceHealth(BaseModel):
    source_id: str
    last_successful_fetch: Optional[str] = None
    last_failed_fetch: Optional[str] = None
    response_latency_ms: Optional[float] = None
    retrieved_count: int = 0
    error_count: int = 0
    rate_limited_count: int = 0
    consecutive_failures: int = 0
    current_status: SourceAccessStatus = SourceAccessStatus.AVAILABLE_PUBLIC
    status_message: Optional[str] = None
    last_checked_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class EmployerCareerSource(BaseModel):
    id: str = Field(default_factory=lambda: f"emp_{uuid4().hex[:8]}")
    employer_name: str
    career_url: str
    provider_type: Optional[ConnectorId] = None
    board_token: Optional[str] = None
    approved_origin: str
    last_validated_at: Optional[str] = None
    access_status: SourceAccessStatus = SourceAccessStatus.UNVERIFIED
    is_enabled: bool = True
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# =============================================================================
# Extraction & Field Provenance Models
# =============================================================================

class FieldProvenance(BaseModel):
    source_id: str
    retrieved_at: str
    raw_field_path: str
    parser_method: str
    confidence: ExtractionConfidence = ExtractionConfidence.HIGH
    is_transformed: bool = False
    original_raw_value: Optional[str] = None


class ExtractedCompensation(BaseModel):
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    currency: Optional[str] = None
    unit: Optional[str] = None  # annual, hourly, monthly, etc.
    pay_period: Optional[str] = None
    compensation_type: Optional[str] = None
    raw_text: Optional[str] = None


class ExtractedLocation(BaseModel):
    country: Optional[str] = None
    state_region: Optional[str] = None
    city: Optional[str] = None
    office: Optional[str] = None
    is_remote: bool = False
    workplace_type: Optional[str] = None  # remote, hybrid, onsite, flexible
    raw_location_text: Optional[str] = None


class ExtractedPosting(BaseModel):
    native_posting_id: str
    title: str
    employer_name: str
    official_posting_url: str
    application_url: Optional[str] = None
    location: ExtractedLocation = Field(default_factory=ExtractedLocation)
    employment_type: Optional[str] = None  # full_time, part_time, internship, contract
    compensation: Optional[ExtractedCompensation] = None
    posted_date: Optional[str] = None
    updated_date: Optional[str] = None
    closing_date: Optional[str] = None
    department: Optional[str] = None
    office: Optional[str] = None
    description_text: str = ""
    description_html: Optional[str] = None
    raw_source_data: dict[str, Any] = Field(default_factory=dict)
    provenance: dict[str, FieldProvenance] = Field(default_factory=dict)


# =============================================================================
# Observation & Snapshot Models
# =============================================================================

class JobSourceObservation(BaseModel):
    id: str = Field(default_factory=lambda: f"obs_{uuid4().hex[:12]}")
    source_id: str
    provider: ConnectorId
    native_posting_id: str
    source_url: str
    title: str
    employer: str
    location: ExtractedLocation = Field(default_factory=ExtractedLocation)
    employment_type: Optional[str] = None
    compensation: Optional[ExtractedCompensation] = None
    description_text: str = ""
    application_url: Optional[str] = None
    department: Optional[str] = None
    posted_at: Optional[str] = None
    updated_at: Optional[str] = None
    discovered_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_fetched_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    availability: PostingAvailability = PostingAvailability.AVAILABLE
    prefilter_status: PrefilterOutcome = PrefilterOutcome.UNKNOWN
    prefilter_reasons: list[str] = Field(default_factory=list)
    snapshot_id: Optional[str] = None
    extraction_version: str = "1.0.0"
    raw_data_ref: Optional[str] = None


class JobSourceSnapshot(BaseModel):
    id: str = Field(default_factory=lambda: f"snp_{uuid4().hex[:12]}")
    source_id: str
    task_id: str
    completeness: SnapshotCompleteness = SnapshotCompleteness.COMPLETE
    total_observed: int = 0
    new_count: int = 0
    updated_count: int = 0
    unchanged_count: int = 0
    closed_count: int = 0
    started_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: Optional[str] = None
    cursor: Optional[str] = None
    error_message: Optional[str] = None


# =============================================================================
# Discovery Task Models
# =============================================================================

class DiscoveryTaskRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"task_{uuid4().hex[:10]}")
    strategy_id: Optional[str] = None
    requested_sources: list[str] = Field(default_factory=list)
    selected_sources: list[str] = Field(default_factory=list)
    status: DiscoveryTaskState = DiscoveryTaskState.CREATED
    started_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: Optional[str] = None
    total_postings_found: int = 0
    new_postings_count: int = 0
    errors: list[str] = Field(default_factory=list)
    cancellation_requested: bool = False
    source_snapshots: dict[str, str] = Field(default_factory=dict)  # source_id -> snapshot_id


# =============================================================================
# Settings & Overview DTOs
# =============================================================================

class DiscoverySettingsConfig(BaseModel):
    max_concurrent_sources: int = 4
    per_source_request_rpm: int = 30
    request_timeout_seconds: int = 20
    max_postings_per_task: int = 200
    max_browser_sessions: int = 1
    cache_duration_minutes: int = 60
    allow_browser_fallback: bool = True
    enforce_ssrf_protection: bool = True
    local_only_preference: bool = False


class DiscoveryOverviewStats(BaseModel):
    total_sources: int = 0
    enabled_sources: int = 0
    total_observations: int = 0
    active_postings_count: int = 0
    recently_discovered_count: int = 0
    failed_sources_count: int = 0
    rate_limited_sources_count: int = 0
    active_tasks_count: int = 0


# =============================================================================
# Request / Response DTOs
# =============================================================================

class JobSourceCreateRequest(BaseModel):
    name: str
    connector_id: ConnectorId
    official_domain: str
    board_token: Optional[str] = None
    site_id: Optional[str] = None
    feed_url: Optional[str] = None
    employer_name: Optional[str] = None
    category: SourceCategory = SourceCategory.EMPLOYER_ATS_BOARD
    is_enabled: bool = True
    rate_limit_rpm: int = 30
    custom_headers: dict[str, str] = Field(default_factory=dict)
    custom_params: dict[str, Any] = Field(default_factory=dict)


class JobSourceUpdateRequest(BaseModel):
    name: Optional[str] = None
    board_token: Optional[str] = None
    site_id: Optional[str] = None
    feed_url: Optional[str] = None
    employer_name: Optional[str] = None
    is_enabled: Optional[bool] = None
    rate_limit_rpm: Optional[int] = None
    custom_headers: Optional[dict[str, str]] = None
    custom_params: Optional[dict[str, Any]] = None


class DiscoveryTaskCreateRequest(BaseModel):
    strategy_id: Optional[str] = None
    source_ids: list[str] = Field(default_factory=list)
    keywords: list[str] = Field(default_factory=list)
    location_filter: Optional[str] = None
    work_arrangement: Optional[str] = None
    max_postings: int = 100


class UrlImportRequest(BaseModel):
    url: str
    employer_name: Optional[str] = None
    target_role: Optional[str] = None
    notes: Optional[str] = None


class ManualImportRequest(BaseModel):
    title: str
    employer_name: str
    source_url: Optional[str] = None
    location: Optional[str] = None
    work_arrangement: Optional[str] = None
    employment_type: Optional[str] = None
    compensation_text: Optional[str] = None
    description: str
    application_url: Optional[str] = None
    notes: Optional[str] = None


class EmployerCareerPageCreateRequest(BaseModel):
    employer_name: str
    career_url: str


class SourceValidationResult(BaseModel):
    source_id: str
    is_valid: bool
    detected_connector: Optional[ConnectorId] = None
    access_status: SourceAccessStatus
    available_postings_count: Optional[int] = None
    response_latency_ms: Optional[float] = None
    message: str
