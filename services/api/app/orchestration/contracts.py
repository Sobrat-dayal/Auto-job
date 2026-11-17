"""Pydantic data models, contracts, and enums for multi-agent orchestration (Stage 12)."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class WorkflowStatus(str, Enum):
    """Lifecycle states of an autonomous multi-agent workflow."""

    CREATED = "created"
    PLANNING = "planning"
    PLAN_READY = "plan_ready"
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_FOR_DEPENDENCIES = "waiting_for_dependencies"
    WAITING_FOR_AUTHORIZATION = "waiting_for_authorization"
    PAUSED = "paused"
    RECOVERING = "recovering"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    PARTIALLY_COMPLETED = "partially_completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

    @property
    def is_active(self) -> bool:
        return self in (
            WorkflowStatus.PLANNING,
            WorkflowStatus.QUEUED,
            WorkflowStatus.RUNNING,
            WorkflowStatus.WAITING_FOR_DEPENDENCIES,
            WorkflowStatus.RECOVERING,
            WorkflowStatus.VERIFYING,
        )

    @property
    def is_terminal(self) -> bool:
        return self in (
            WorkflowStatus.COMPLETED,
            WorkflowStatus.PARTIALLY_COMPLETED,
            WorkflowStatus.FAILED,
            WorkflowStatus.CANCELLED,
        )


class StepStatus(str, Enum):
    """Execution status of an individual workflow step node."""

    PENDING = "pending"
    READY = "ready"
    ASSIGNED = "assigned"
    RUNNING = "running"
    VERIFYING = "verifying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED = "blocked"
    PAUSED = "paused"

    @property
    def is_terminal(self) -> bool:
        return self in (
            StepStatus.COMPLETED,
            StepStatus.FAILED,
            StepStatus.CANCELLED,
            StepStatus.BLOCKED,
        )


class PriorityLevel(str, Enum):
    """Task and workflow priority levels."""

    CRITICAL = "critical"
    INTERACTIVE = "interactive"
    HIGH = "high"
    NORMAL = "normal"
    BACKGROUND = "background"


class FailureCategory(str, Enum):
    """Normalized taxonomy of execution and runtime failures."""

    PROVIDER_UNAVAILABLE = "provider_unavailable"
    MODEL_UNAVAILABLE = "model_unavailable"
    TIMEOUT = "timeout"
    RATE_LIMIT = "rate_limit"
    INVALID_OUTPUT = "invalid_output"
    FAILED_VERIFICATION = "failed_verification"
    MISSING_CAPABILITY = "missing_capability"
    RESOURCE_EXHAUSTED = "resource_exhausted"
    AUTHORIZATION_REQUIRED = "authorization_required"
    DEPENDENCY_FAILURE = "dependency_failure"
    BACKEND_INTERRUPTION = "backend_interruption"
    CANCELLED_BY_USER = "cancelled_by_user"
    UNKNOWN_EXTERNAL_OUTCOME = "unknown_external_outcome"


class VerificationStatus(str, Enum):
    """Outcome of step verification."""

    PASS = "pass"
    FAIL = "fail"
    NEEDS_REVIEW = "needs_review"
    UNVERIFIABLE = "unverifiable"


class VerificationPolicy(str, Enum):
    """Declared verification policy for capabilities and steps."""

    SCHEMA_VALIDATION = "schema_validation"
    DETERMINISTIC_ASSERTION = "deterministic_assertion"
    OUTPUT_CONTRACT = "output_contract"
    SEMANTIC_REVIEW = "semantic_review"
    ARTIFACT_VALIDATION = "artifact_validation"
    HUMAN_JUDGMENT = "human_judgment"


class MessageType(str, Enum):
    """Typed agent-to-agent communication categories."""

    TASK_ASSIGNMENT = "task_assignment"
    TASK_RESULT = "task_result"
    PROGRESS_UPDATE = "progress_update"
    VERIFICATION_REQUEST = "verification_request"
    VERIFICATION_RESULT = "verification_result"
    ERROR_REPORT = "error_report"
    RECOVERY_PROPOSAL = "recovery_proposal"
    CAPABILITY_UNAVAILABLE = "capability_unavailable"


# ---------------------------------------------------------------------------
# Core Workflow Schemas
# ---------------------------------------------------------------------------


class WorkflowStepDefinition(BaseModel):
    """Definition of an individual step within a workflow plan."""

    step_id: str = Field(description="Unique identifier of step within plan (e.g. 'step_1')")
    title: str = Field(description="Human-readable title")
    description: str = Field(default="", description="Detailed execution instruction")
    capability_id: str = Field(description="Required capability (e.g. 'text_summarize', 'structured_extract')")
    dependencies: list[str] = Field(default_factory=list, description="List of step_ids that must complete before this step")
    input_bindings: dict[str, Any] = Field(default_factory=dict, description="Inputs with literal or mustache '{{step_x.field}}' references")
    expected_output_schema: dict[str, Any] | None = Field(default=None, description="Optional JSON Schema for validation")
    verification_policy: VerificationPolicy = Field(default=VerificationPolicy.SCHEMA_VALIDATION)
    timeout_seconds: int = Field(default=60, ge=5, le=600)
    max_retries: int = Field(default=2, ge=0, le=5)
    requires_authorization: bool = Field(default=False)
    priority: PriorityLevel = Field(default=PriorityLevel.NORMAL)


class WorkflowPlan(BaseModel):
    """Structured execution plan produced by PlanningAgent."""

    workflow_id: str
    version: int = Field(default=1, ge=1)
    goal: str
    steps: list[WorkflowStepDefinition] = Field(default_factory=list)
    success_criteria: list[str] = Field(default_factory=list)
    max_duration_seconds: int = Field(default=300, ge=30, le=3600)
    max_total_steps: int = Field(default=20, ge=1, le=50)
    max_parallel_steps: int = Field(default=4, ge=1, le=10)


class WorkflowCreateRequest(BaseModel):
    """Request payload to initiate a new autonomous workflow."""

    goal: str = Field(min_length=5, max_length=4000, description="Natural language goal statement")
    title: str | None = Field(default=None, max_length=256)
    constraints: dict[str, Any] = Field(default_factory=dict)
    priority: PriorityLevel = Field(default=PriorityLevel.NORMAL)
    model_preference: str | None = Field(default=None)
    is_local_only: bool = Field(default=False)


class WorkflowReplanRequest(BaseModel):
    """Request payload to trigger controlled dynamic replanning."""

    reason: str = Field(min_length=3, max_length=1000)
    failed_step_id: str | None = Field(default=None)
    additional_constraints: dict[str, Any] = Field(default_factory=dict)


class WorkflowStepResponse(BaseModel):
    """Current state of a workflow step node."""

    id: str
    workflow_id: str
    plan_id: str
    step_id: str
    title: str
    description: str
    capability_id: str
    assigned_agent_id: str | None = None
    status: StepStatus
    dependencies: list[str] = Field(default_factory=list)
    input_bindings: dict[str, Any] = Field(default_factory=dict)
    output_result: dict[str, Any] | None = None
    error_info: dict[str, Any] | None = None
    verification_status: VerificationStatus | None = None
    retry_count: int = 0
    max_retries: int = 2
    timeout_seconds: int = 60
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime


class WorkflowResponse(BaseModel):
    """Comprehensive workflow response payload."""

    id: str
    title: str
    goal: str
    status: WorkflowStatus
    priority: PriorityLevel
    active_plan_id: str | None = None
    active_plan: WorkflowPlan | None = None
    steps: list[WorkflowStepResponse] = Field(default_factory=list)
    context: dict[str, Any] = Field(default_factory=dict)
    constraints: dict[str, Any] = Field(default_factory=dict)
    total_steps: int = 0
    completed_steps: int = 0
    failed_steps: int = 0
    total_cost_usd: float = 0.0
    total_tokens: int = 0
    error_message: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None
    updated_at: datetime


class WorkflowSummary(BaseModel):
    """Compact summary of a workflow for listing screens."""

    id: str
    title: str
    goal: str
    status: WorkflowStatus
    priority: PriorityLevel
    total_steps: int
    completed_steps: int
    failed_steps: int
    total_cost_usd: float
    created_at: datetime
    updated_at: datetime


# ---------------------------------------------------------------------------
# Agent & Capability Schemas
# ---------------------------------------------------------------------------


class AgentDefinition(BaseModel):
    """Specification of an autonomous coordination or specialist agent."""

    agent_id: str
    name: str
    role: str
    description: str
    capabilities: list[str] = Field(default_factory=list)
    supported_task_types: list[str] = Field(default_factory=list)
    required_permissions: list[str] = Field(default_factory=list)
    concurrency_limit: int = Field(default=1, ge=1)
    model_preference: str | None = None
    is_available: bool = True
    enabled: bool = True
    implementation_version: str = "0.1.0"
    roadmap_stage: str = "Stage 12"


class CapabilityDefinition(BaseModel):
    """Specification of a discrete registered capability."""

    capability_id: str
    name: str
    version: str = "1.0.0"
    description: str
    input_schema: dict[str, Any] = Field(default_factory=dict)
    output_schema: dict[str, Any] = Field(default_factory=dict)
    requires_ai: bool = False
    is_deterministic: bool = True
    default_verification_policy: VerificationPolicy = VerificationPolicy.SCHEMA_VALIDATION
    timeout_seconds: int = 60
    idempotent: bool = True


# ---------------------------------------------------------------------------
# Verification & Recovery Schemas
# ---------------------------------------------------------------------------


class VerificationResult(BaseModel):
    """Structured audit evidence produced by VerificationAgent."""

    verification_id: str = Field(default_factory=lambda: str(uuid4()))
    step_id: str
    verification_type: str = "deterministic"
    status: VerificationStatus
    passed: bool
    score: float | None = None
    evidence: dict[str, Any] = Field(default_factory=dict)
    details: str | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RecoveryAction(BaseModel):
    """Decision proposed by RecoveryAgent."""

    action: str = Field(description="'retry', 'alternate_model', 'replan', 'fail', 'wait_authorization'")
    failure_category: FailureCategory
    reason: str
    step_id: str
    attempt_number: int = 1
    safe_to_retry: bool = True
    alternate_provider: str | None = None
    alternate_model: str | None = None


class AgentMessage(BaseModel):
    """Typed message exchanged across coordination agents or event bus."""

    message_id: str = Field(default_factory=lambda: str(uuid4()))
    workflow_id: str
    sender_agent_id: str
    recipient_agent_id: str
    step_id: str | None = None
    message_type: MessageType
    payload: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
