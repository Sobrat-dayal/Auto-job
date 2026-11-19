"""Data contracts, enums, and models for Job Aggregation Engine (Stage 27)."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Optional
from uuid import uuid4
from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class EmployerIdentityStatus(StrEnum):
    VERIFIED = "verified"
    USER_CONFIRMED = "user_confirmed"
    STRONGLY_SUPPORTED = "strongly_supported"
    PROBABLE = "probable"
    AMBIGUOUS = "ambiguous"
    UNKNOWN = "unknown"
    CONFLICTED = "conflicted"
    REJECTED = "rejected"


class OrganizationType(StrEnum):
    DIRECT_EMPLOYER = "direct_employer"
    STAFFING_AGENCY = "staffing_agency"
    RECRUITING_FIRM = "recruiting_firm"
    EMPLOYER_OF_RECORD = "employer_of_record"
    UNKNOWN = "unknown"


class CanonicalJobStatus(StrEnum):
    ACTIVE = "active"
    POSSIBLY_ACTIVE = "possibly_active"
    CLOSED = "closed"
    EXPIRED = "expired"
    REMOVED = "removed"
    UNKNOWN = "unknown"
    CONFLICTED = "conflicted"


class JobIdentityStatus(StrEnum):
    VERIFIED = "verified"
    USER_CONFIRMED = "user_confirmed"
    STRONGLY_SUPPORTED = "strongly_supported"
    PROBABLE = "probable"
    AMBIGUOUS = "ambiguous"
    UNKNOWN = "unknown"
    CONFLICTED = "conflicted"
    REJECTED = "rejected"


class ConflictState(StrEnum):
    NO_CONFLICT = "no_conflict"
    HAS_CONFLICTS = "has_conflicts"
    CONFLICTS_RESOLVED = "conflicts_resolved"


class DuplicateDecisionState(StrEnum):
    CONFIRMED_DUPLICATE = "confirmed_duplicate"
    STRONG_DUPLICATE_CANDIDATE = "strong_duplicate_candidate"
    POSSIBLE_DUPLICATE = "possible_duplicate"
    RELATED_BUT_DISTINCT = "related_but_distinct"
    CONFIRMED_DISTINCT = "confirmed_distinct"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"
    CONFLICT = "conflict"
    NOT_EVALUATED = "not_evaluated"


class DuplicateAction(StrEnum):
    MERGE = "merge"
    KEEP_SEPARATE = "keep_separate"
    MARK_RELATED = "mark_related"
    DEFER = "defer"
    REQUEST_MORE_EVIDENCE = "request_more_evidence"


class ConflictType(StrEnum):
    SALARY_MISMATCH = "salary_mismatch"
    LOCATION_MISMATCH = "location_mismatch"
    EMPLOYMENT_TYPE_MISMATCH = "employment_type_mismatch"
    STATUS_MISMATCH = "status_mismatch"
    REMOTE_MISMATCH = "remote_mismatch"
    REQUISITION_MISMATCH = "requisition_mismatch"


class ConflictResolutionStatus(StrEnum):
    NO_CONFLICT = "no_conflict"
    MISSING_FROM_SOURCE = "missing_from_source"
    EQUIVALENT_AFTER_NORMALIZATION = "equivalent_after_normalization"
    SOURCE_OUTDATED = "source_outdated"
    RESOLVED_BY_AUTHORITY_RULE = "resolved_by_authority_rule"
    RESOLVED_BY_USER = "resolved_by_user"
    UNRESOLVED = "unresolved"
    IDENTITY_CONFLICT = "identity_conflict"


class JobRelationshipType(StrEnum):
    SIMILAR_ROLE = "similar_role"
    SAME_EMPLOYER = "same_employer"
    SAME_HIRING_CAMPAIGN = "same_hiring_campaign"
    SAME_REQUISITION_GROUP = "same_requisition_group"
    REPOSTED_VERSION = "reposted_version"
    MULTI_LOCATION_RELATED = "multi_location_related"
    DISTINCT_OPENING = "distinct_opening"


class AggregationTaskType(StrEnum):
    INCREMENTAL = "incremental"
    FULL_SYNC = "full_sync"
    SOURCE_SYNC = "source_sync"
    SINGLE_OBSERVATION = "single_observation"


class AggregationTaskStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# =============================================================================
# Models: Employer Identity & Structure
# =============================================================================

class EmployerIdentityEvidence(BaseModel):
    evidence_type: str
    source_reference: str
    observed_value: str
    verification_status: str = "probable"
    confidence_delta: float = 0.0


class CanonicalEmployerRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"emp_{uuid4().hex[:12]}")
    name: str
    legal_name: Optional[str] = None
    organization_type: OrganizationType = OrganizationType.DIRECT_EMPLOYER
    identity_status: EmployerIdentityStatus = EmployerIdentityStatus.PROBABLE
    official_careers_url: Optional[str] = None
    primary_domain: Optional[str] = None
    confidence_score: float = 0.8
    aliases: list[str] = Field(default_factory=list)
    verified_domains: list[str] = Field(default_factory=list)
    provider_boards: list[dict[str, str]] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# =============================================================================
# Models: Canonical Job & Source Links
# =============================================================================

class CanonicalJobLocationRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"loc_{uuid4().hex[:8]}")
    country: Optional[str] = None
    region: Optional[str] = None
    city: Optional[str] = None
    office: Optional[str] = None
    is_remote: bool = False
    workplace_type: Optional[str] = None
    raw_text: Optional[str] = None
    source_id: Optional[str] = None


class CanonicalJobIdentifierRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"ident_{uuid4().hex[:8]}")
    id_type: str
    raw_id: str
    normalized_id: str
    namespace: str
    source_id: Optional[str] = None


class CanonicalJobSourceLinkRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"link_{uuid4().hex[:10]}")
    canonical_job_id: str
    listing_id: Optional[str] = None
    source_observation_id: str
    source_id: str
    provider: str
    native_posting_id: str
    original_url: str
    application_url: Optional[str] = None
    association_status: str = "active"
    decision_method: str = "exact_rule"
    evidence: dict[str, Any] = Field(default_factory=dict)
    is_primary: bool = False
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class CanonicalJobConflictRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"conf_{uuid4().hex[:8]}")
    field_name: str
    conflict_type: ConflictType
    status: ConflictResolutionStatus = ConflictResolutionStatus.UNRESOLVED
    source_values: dict[str, Any] = Field(default_factory=dict)
    resolution_note: Optional[str] = None
    resolved_by: Optional[str] = None
    resolved_at: Optional[str] = None


class CanonicalJobRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"cjob_{uuid4().hex[:12]}")
    employer_id: Optional[str] = None
    employer_name: str
    display_title: str
    normalized_title: str
    requisition_id: Optional[str] = None
    employment_type: Optional[str] = None
    location_summary: Optional[str] = None
    work_arrangement: Optional[str] = None
    description_reference: Optional[str] = None
    compensation_summary: Optional[str] = None
    status: CanonicalJobStatus = CanonicalJobStatus.ACTIVE
    first_observed_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_observed_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    last_verified_active_at: Optional[str] = None
    version: int = 1
    source_count: int = 1
    identity_status: JobIdentityStatus = JobIdentityStatus.PROBABLE
    conflict_state: ConflictState = ConflictState.NO_CONFLICT
    primary_source_id: Optional[str] = None
    primary_url: Optional[str] = None
    is_evergreen: bool = False
    is_repost: bool = False
    sources: list[CanonicalJobSourceLinkRecord] = Field(default_factory=list)
    locations: list[CanonicalJobLocationRecord] = Field(default_factory=list)
    identifiers: list[CanonicalJobIdentifierRecord] = Field(default_factory=list)
    conflicts: list[CanonicalJobConflictRecord] = Field(default_factory=list)
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# =============================================================================
# Models: Duplicate Detection & Assessment
# =============================================================================

class DuplicateAssessment(BaseModel):
    left_job_id: str
    right_job_id: str
    proposed_status: DuplicateDecisionState = DuplicateDecisionState.POSSIBLE_DUPLICATE
    similarity_score: float = 0.0
    positive_evidence: list[dict[str, Any]] = Field(default_factory=list)
    negative_evidence: list[dict[str, Any]] = Field(default_factory=list)
    missing_evidence: list[str] = Field(default_factory=list)
    rule_version: str = "1.0.0"
    review_required: bool = False
    recommended_action: DuplicateAction = DuplicateAction.DEFER
    explanation: str = ""


class DuplicateCandidateRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"dup_{uuid4().hex[:10]}")
    left_job_id: str
    right_job_id: str
    status: DuplicateDecisionState = DuplicateDecisionState.POSSIBLE_DUPLICATE
    similarity_score: float = 0.0
    matching_factors: dict[str, Any] = Field(default_factory=dict)
    contradictions: dict[str, Any] = Field(default_factory=dict)
    recommended_action: DuplicateAction = DuplicateAction.DEFER
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


# =============================================================================
# Models: Merge and Split Operations
# =============================================================================

class MergePreviewRequest(BaseModel):
    surviving_job_id: str
    superseded_job_id: str
    preferred_employer_id: Optional[str] = None
    preferred_title: Optional[str] = None


class MergePreviewResponse(BaseModel):
    surviving_job_id: str
    superseded_job_id: str
    proposed_title: str
    proposed_employer_id: Optional[str] = None
    resulting_source_count: int
    source_links_to_transfer: list[str] = Field(default_factory=list)
    detected_conflicts: list[dict[str, Any]] = Field(default_factory=list)
    affected_downstream_references: list[dict[str, Any]] = Field(default_factory=list)
    is_safe_to_merge: bool = True
    warnings: list[str] = Field(default_factory=list)


class MergeExecuteRequest(BaseModel):
    surviving_job_id: str
    superseded_job_id: str
    reason: str = "Authorized duplicate merge"
    actor: str = "user_manual"
    field_overrides: dict[str, Any] = Field(default_factory=dict)


class MergeExecuteResponse(BaseModel):
    operation_id: str
    surviving_job: CanonicalJobRecord
    superseded_job_id: str
    status: str = "completed"
    transferred_source_count: int
    created_alias_id: str


class SplitPreviewResponse(BaseModel):
    source_job_id: str
    source_links: list[CanonicalJobSourceLinkRecord]
    proposed_split_groups: list[dict[str, Any]]
    affected_references_warning: list[str] = Field(default_factory=list)


class SplitExecuteRequest(BaseModel):
    source_job_id: str
    source_link_ids_to_detach: list[str]
    reason: str = "Reversing incorrect merge / separating distinct requisition"
    actor: str = "user_manual"


class SplitExecuteResponse(BaseModel):
    operation_id: str
    original_job_id: str
    new_canonical_job_ids: list[str]
    status: str = "completed"


# =============================================================================
# Models: Review & Corrections
# =============================================================================

class DuplicateReviewSubmitRequest(BaseModel):
    candidate_id: str
    decision: DuplicateAction  # merge, keep_separate, mark_related, defer
    reason: str = "User reviewed decision"
    decided_by: str = "user_manual"


class EmployerCorrectionRequest(BaseModel):
    employer_id: str
    name: Optional[str] = None
    legal_name: Optional[str] = None
    organization_type: Optional[OrganizationType] = None
    official_careers_url: Optional[str] = None
    add_alias: Optional[str] = None
    add_domain: Optional[str] = None


class ConflictResolveRequest(BaseModel):
    conflict_id: str
    chosen_value: Any
    resolution_note: str = "Resolved by user"
    resolved_by: str = "user_manual"


# =============================================================================
# Models: Tasks & Diagnostics
# =============================================================================

class AggregationOverviewStats(BaseModel):
    total_source_observations: int = 0
    total_canonical_jobs: int = 0
    multi_source_canonical_jobs: int = 0
    pending_duplicate_reviews: int = 0
    confirmed_duplicate_merges: int = 0
    unresolved_employer_identities: int = 0
    active_field_conflicts: int = 0
    running_tasks: int = 0
    last_sync_timestamp: Optional[str] = None


class AggregationTaskRecord(BaseModel):
    id: str = Field(default_factory=lambda: f"aggtask_{uuid4().hex[:8]}")
    task_type: AggregationTaskType = AggregationTaskType.INCREMENTAL
    status: AggregationTaskStatus = AggregationTaskStatus.PENDING
    observations_total: int = 0
    observations_processed: int = 0
    canonical_jobs_created: int = 0
    canonical_jobs_updated: int = 0
    duplicates_found: int = 0
    merges_performed: int = 0
    reviews_queued: int = 0
    conflicts_detected: int = 0
    error_message: Optional[str] = None
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class AggregationSettingsConfig(BaseModel):
    auto_merge_enabled: bool = True
    min_similarity_for_candidate: float = 0.75
    min_similarity_for_auto_merge: float = 0.92
    require_same_requisition: bool = True
    enable_ai_assisted_review: bool = True
    batch_size: int = 50
    worker_concurrency: int = 2
    updated_at: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())


class AggregationDiagnosticsReport(BaseModel):
    status: str = "healthy"
    database_connected: bool = True
    canonical_jobs_count: int = 0
    canonical_employers_count: int = 0
    active_conflicts_count: int = 0
    unresolved_candidates_count: int = 0
    recent_tasks: list[AggregationTaskRecord] = Field(default_factory=list)
    system_timestamp: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
