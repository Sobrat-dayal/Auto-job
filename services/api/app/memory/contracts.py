"""Contracts, enums, and data transfer schemas for the Stage 15 Memory Engine."""

from datetime import UTC, datetime
from enum import Enum
import hashlib
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field


class MemoryType(str, Enum):
    """Core memory taxonomy."""

    WORKING = "working"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"
    PROCEDURAL = "procedural"


class MemoryScope(str, Enum):
    """Access boundary scopes for memories."""

    USER = "user"
    APPLICANT_PROFILE = "applicant_profile"
    WORKFLOW = "workflow"
    TASK = "task"
    AGENT = "agent"
    PROJECT = "project"
    INTEGRATION = "integration"
    SHARED = "shared"


class VerificationStatus(str, Enum):
    """Epistemic verification state of a memory record."""

    VERIFIED = "verified"
    USER_CONFIRMED = "user_confirmed"
    EVIDENCE_SUPPORTED = "evidence_supported"
    UNVERIFIED = "unverified"
    CONFLICTED = "conflicted"
    SUPERSEDED = "superseded"
    EXPIRED = "expired"
    REJECTED = "rejected"


class ConfidenceCategory(str, Enum):
    """Confidence tier assigned to a memory claim."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    UNRATED = "unrated"


class SensitivityCategory(str, Enum):
    """Data classification and privacy tier."""

    PUBLIC = "public"
    INTERNAL = "internal"
    PERSONAL = "personal"
    SENSITIVE = "sensitive"
    RESTRICTED = "restricted"
    SECRET = "secret"


class VisibilityPolicy(str, Enum):
    """Visibility boundaries across agents and sessions."""

    SCOPED = "scoped"
    SHARED = "shared"
    PRIVATE = "private"


class SearchMode(str, Enum):
    """Retrieval pipeline mode."""

    HYBRID = "hybrid"
    SEMANTIC = "semantic"
    KEYWORD = "keyword"


class RetentionPolicy(str, Enum):
    """Configured lifecycle retention duration."""

    PERMANENT = "permanent"
    SESSION = "session"
    TASK = "task"
    WORKFLOW = "workflow"
    THIRTY_DAYS = "30_days"
    NINETY_DAYS = "90_days"
    ONE_YEAR = "1_year"


class EmbeddingStatus(str, Enum):
    """Status of vector embedding calculation."""

    PENDING = "pending"
    COMPLETED = "completed"
    FAILED = "failed"
    NOT_REQUIRED = "not_required"


# ---------------------------------------------------------------------------
# Request and Response Models
# ---------------------------------------------------------------------------

class ProvenanceMetadata(BaseModel):
    """Traceable provenance and evidence references for a memory."""

    source_type: str = "user_statement"
    source_ref: str = ""
    author: Optional[str] = None
    original_workflow_id: Optional[str] = None
    original_task_id: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
    extra: dict[str, Any] = Field(default_factory=dict)


class MemoryCreateRequest(BaseModel):
    """Request payload to create a new persistent memory record."""

    memory_type: MemoryType = MemoryType.SEMANTIC
    title: str = Field(..., min_length=1, max_length=256)
    content: str = Field(..., min_length=1)
    summary: str = ""
    owner_scope: MemoryScope = MemoryScope.USER
    scope_id: str = Field(..., min_length=1, max_length=128)
    source_type: str = "user_statement"
    source_ref: str = ""
    provenance: Optional[ProvenanceMetadata] = None
    verification_status: VerificationStatus = VerificationStatus.UNVERIFIED
    confidence_category: ConfidenceCategory = ConfidenceCategory.MEDIUM
    sensitivity_category: SensitivityCategory = SensitivityCategory.INTERNAL
    visibility_policy: VisibilityPolicy = VisibilityPolicy.SCOPED
    retention_policy: RetentionPolicy = RetentionPolicy.PERMANENT
    metadata: dict[str, Any] = Field(default_factory=dict)
    generate_embedding: bool = True


class MemoryUpdateRequest(BaseModel):
    """Request payload to update an existing memory record."""

    title: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    verification_status: Optional[VerificationStatus] = None
    confidence_category: Optional[ConfidenceCategory] = None
    sensitivity_category: Optional[SensitivityCategory] = None
    visibility_policy: Optional[VisibilityPolicy] = None
    retention_policy: Optional[RetentionPolicy] = None
    superseded_by: Optional[str] = None
    metadata: Optional[dict[str, Any]] = None


class MemoryRecordResponse(BaseModel):
    """Serialized memory record representation."""

    id: str
    memory_type: MemoryType
    title: str
    content: str
    summary: str
    owner_scope: MemoryScope
    scope_id: str
    source_type: str
    source_ref: str
    provenance: dict[str, Any]
    verification_status: VerificationStatus
    confidence_category: ConfidenceCategory
    sensitivity_category: SensitivityCategory
    visibility_policy: VisibilityPolicy
    created_at: datetime
    updated_at: datetime
    last_accessed_at: datetime
    expires_at: Optional[datetime] = None
    superseded_by: Optional[str] = None
    version: int
    embedding_model_id: str
    embedding_version: int
    embedding_status: EmbeddingStatus
    content_checksum: str
    retention_policy: RetentionPolicy
    is_deleted: bool
    metadata: dict[str, Any]


class MemorySearchRequest(BaseModel):
    """Search request supporting hybrid, vector, and keyword queries with filters."""

    query: str = Field(..., min_length=1)
    search_mode: SearchMode = SearchMode.HYBRID
    memory_types: Optional[list[MemoryType]] = None
    owner_scope: Optional[MemoryScope] = None
    scope_id: Optional[str] = None
    min_verification_status: Optional[VerificationStatus] = None
    max_sensitivity: Optional[SensitivityCategory] = None
    limit: int = Field(default=10, ge=1, le=100)
    min_score: float = Field(default=0.0, ge=0.0, le=1.0)
    metadata_filters: dict[str, Any] = Field(default_factory=dict)
    exclude_superseded: bool = True
    agent_id: Optional[str] = None
    workflow_id: Optional[str] = None


class MemorySearchResultItem(BaseModel):
    """Individual item returned in a search response."""

    memory_id: str
    title: str
    content_snippet: str
    memory_type: MemoryType
    owner_scope: MemoryScope
    scope_id: str
    verification_status: VerificationStatus
    sensitivity_category: SensitivityCategory
    similarity_score: float = 0.0
    keyword_score: float = 0.0
    combined_score: float = 0.0
    provenance: dict[str, Any] = Field(default_factory=dict)
    created_at: datetime


class MemorySearchResponse(BaseModel):
    """Container for search results and execution diagnostics."""

    results: list[MemorySearchResultItem]
    query: str
    search_mode: SearchMode
    total_matched: int
    latency_ms: float


class ContextBuildRequest(BaseModel):
    """Request to assemble bounded, relevant memory context for an agent execution."""

    task_description: str
    agent_role: str
    workflow_id: Optional[str] = None
    max_tokens: int = Field(default=1500, ge=100, le=8000)
    scope_ids: list[str] = Field(default_factory=list)
    memory_types: Optional[list[MemoryType]] = None


class ContextBuildResponse(BaseModel):
    """Assembled structured context payload for model prompts."""

    context_text: str
    records_used: list[str]
    total_tokens: int
    facts_count: int
    procedures_count: int
    episodes_count: int
    truncated: bool


class ProceduralStep(BaseModel):
    """A single structured execution step within a procedural memory."""

    step_number: int
    name: str
    action: str
    capability_id: str
    parameters_template: dict[str, Any] = Field(default_factory=dict)
    expected_output_key: str = "result"


class ProceduralMemoryCreateRequest(BaseModel):
    """Creation payload for validated reusable procedural workflows."""

    procedure_id: str = Field(..., min_length=1, max_length=64)
    name: str = Field(..., min_length=1, max_length=128)
    description: str = ""
    capability_id: str = Field(..., min_length=1, max_length=64)
    required_inputs: dict[str, Any] = Field(default_factory=dict)
    steps: list[dict[str, Any]] = Field(default_factory=list)
    preconditions: dict[str, Any] = Field(default_factory=dict)
    expected_outputs: dict[str, Any] = Field(default_factory=dict)
    verification_requirements: dict[str, Any] = Field(default_factory=dict)
    required_permissions: list[str] = Field(default_factory=list)
    provenance: dict[str, Any] = Field(default_factory=dict)


class ProceduralMemoryResponse(BaseModel):
    """Serialized representation of a procedural memory."""

    id: str
    procedure_id: str
    name: str
    description: str
    capability_id: str
    required_inputs: dict[str, Any]
    steps: list[dict[str, Any]]
    preconditions: dict[str, Any]
    expected_outputs: dict[str, Any]
    verification_requirements: dict[str, Any]
    required_permissions: list[str]
    provenance: dict[str, Any]
    version: int
    validation_status: str
    success_count: int
    failure_count: int
    created_at: datetime
    updated_at: datetime


class MemoryConflictResponse(BaseModel):
    """Serialized conflict record between contradictory memories."""

    id: str
    memory_id_a: str
    memory_id_b: str
    conflict_type: str
    description: str
    status: str
    resolution_action: Optional[str] = None
    resolved_by: Optional[str] = None
    created_at: datetime
    resolved_at: Optional[datetime] = None


class MemoryConflictResolveRequest(BaseModel):
    """Action to resolve a detected memory conflict."""

    resolution_action: str = Field(..., pattern="^(supersede|keep_both|dismiss|reject)$")
    superseding_memory_id: Optional[str] = None
    notes: Optional[str] = None


class MemoryStatsResponse(BaseModel):
    """System-wide telemetry and storage metrics for agent memory."""

    total_records: int
    by_type: dict[str, int]
    by_verification_status: dict[str, int]
    by_scope: dict[str, int]
    indexed_records: int
    pending_embeddings: int
    conflicts_unresolved: int
    active_procedures: int
    vector_dimension: int
    fts_enabled: bool
