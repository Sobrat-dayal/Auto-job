"""Contracts, data models, enums, and manifest schemas for Specialist AI Agents (Stage 13)."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field

from app.orchestration.contracts import (
    FailureCategory,
    PriorityLevel,
    VerificationPolicy,
    VerificationStatus,
)


class AgentCategory(str, Enum):
    """Categorical classification of agents."""

    ORCHESTRATION = "orchestration"
    RECRUITMENT = "recruitment"
    COMPUTER = "computer"
    DEVELOPMENT = "development"
    RESEARCH = "research"
    PRODUCTIVITY = "productivity"
    CREATIVE = "creative"
    COMMUNICATION = "communication"
    AUTOMATION = "automation"


class AvailabilityState(str, Enum):
    """Operational availability status of an agent."""

    OPERATIONAL = "operational"  # Full executable capability exists
    LIMITED = "limited"          # Safe subset of capabilities is executable
    PLANNED = "planned"          # Defined in roadmap, executable handlers in future stages
    UNAVAILABLE = "unavailable"  # Missing local/cloud prerequisites or connectors
    DISABLED = "disabled"        # Administratively or user-disabled


class AgentModelProfile(BaseModel):
    """AI Gateway inference preferences and resource budget for an agent."""

    preferred_model: str | None = Field(default=None, description="Preferred model identifier or gateway alias")
    task_category: str = Field(default="general", description="Gateway task class (e.g. general, coding, fast, reasoning)")
    local_first: bool = Field(default=True, description="Prefer locally hosted model when eligible")
    cloud_permitted: bool = Field(default=False, description="Whether cloud fallback or routing is authorized")
    fallback_model: str | None = Field(default=None, description="Explicit fallback model")
    max_context_tokens: int = Field(default=4096, ge=512, le=32768)
    max_output_tokens: int = Field(default=2048, ge=64, le=8192)
    temperature: float = Field(default=0.2, ge=0.0, le=1.0)
    timeout_seconds: int = Field(default=60, ge=5, le=300)
    cost_budget_usd: float = Field(default=0.50, ge=0.0)


class AgentContextPolicy(BaseModel):
    """Isolation boundaries and data access policy for an agent."""

    allowed_input_keys: list[str] = Field(default_factory=list, description="Keys permitted in input bindings")
    isolation_level: str = Field(default="strict", description="'strict', 'workflow_scoped', or 'minimal'")
    allow_credentials: bool = Field(default=False, description="Strictly False: specialist agents cannot access raw credentials")
    allow_system_logs: bool = Field(default=False, description="Whether internal system logs may be read")
    retention_policy: str = Field(default="workflow_duration", description="Data retention lifecycle")


class AgentExecutionLimits(BaseModel):
    """Runtime limits and concurrency thresholds."""

    timeout_seconds: int = Field(default=60, ge=5, le=600)
    concurrency_limit: int = Field(default=1, ge=1, le=10)
    max_retries: int = Field(default=2, ge=0, le=5)
    max_model_calls: int = Field(default=3, ge=1, le=10)


class AgentManifest(BaseModel):
    """Complete typed manifest for an autonomous coordination or specialist agent."""

    agent_id: str = Field(description="Unique stable agent slug (e.g. 'job_matching_agent')")
    name: str = Field(description="Human-readable title")
    role: str = Field(description="Functional job title or specialty")
    description: str = Field(description="Detailed operational scope")
    category: AgentCategory
    version: str = Field(default="1.0.0")
    capabilities: list[str] = Field(default_factory=list, description="List of capability IDs this agent provides")
    required_permissions: list[str] = Field(default_factory=list, description="Granted permission scopes")
    allowed_tools: list[str] = Field(default_factory=list, description="Allowlisted tools")
    model_profile: AgentModelProfile = Field(default_factory=AgentModelProfile)
    context_policy: AgentContextPolicy = Field(default_factory=AgentContextPolicy)
    execution_limits: AgentExecutionLimits = Field(default_factory=AgentExecutionLimits)
    verification_policy: VerificationPolicy = Field(default=VerificationPolicy.SCHEMA_VALIDATION)
    availability_state: AvailabilityState = Field(default=AvailabilityState.OPERATIONAL)
    roadmap_stage: str = Field(default="Stage 13 (Active)")
    system_instructions: str = Field(default="")
    instructions_version: str = Field(default="1.0.0")
    enabled: bool = Field(default=True)
    metadata: dict[str, Any] = Field(default_factory=dict)

    @property
    def concurrency_limit(self) -> int:
        return self.execution_limits.concurrency_limit

    @property
    def is_available(self) -> bool:
        return self.enabled and self.availability_state in (
            AvailabilityState.OPERATIONAL,
            AvailabilityState.LIMITED,
        )

    @property
    def supported_task_types(self) -> list[str]:
        return [self.category.value, "execution"]

    @property
    def implementation_version(self) -> str:
        return self.version


class AgentRequest(BaseModel):
    """Standardized invocation request sent to an agent for step execution."""

    workflow_id: str
    step_id: str
    capability_id: str
    input_data: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))


class AgentResult(BaseModel):
    """Standardized normalized execution result produced by a specialist agent."""

    execution_id: str = Field(default_factory=lambda: str(uuid4()))
    agent_id: str
    capability_id: str
    status: str = Field(default="completed", description="'completed', 'failed', 'cancelled'")
    output_data: dict[str, Any] = Field(default_factory=dict)
    artifact_references: list[str] = Field(default_factory=list)
    verification_status: VerificationStatus = Field(default=VerificationStatus.PASS)
    error_category: FailureCategory | None = None
    error_message: str | None = None
    model_used: str | None = None
    tokens_used: int = 0
    duration_ms: int = 0
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AgentHandoff(BaseModel):
    """Typed handoff event between two specialist agents."""

    source_agent_id: str
    target_agent_id: str
    workflow_id: str
    step_id: str
    capability_id: str
    input_payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: str = Field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))


class AgentConfigurationUpdate(BaseModel):
    """Patchable configuration parameters for a specialist agent."""

    enabled: bool | None = None
    preferred_model: str | None = None
    concurrency_limit: int | None = Field(default=None, ge=1, le=10)
    timeout_seconds: int | None = Field(default=None, ge=5, le=600)
    temperature: float | None = Field(default=None, ge=0.0, le=1.0)
    max_tokens: int | None = Field(default=None, ge=64, le=8192)
    local_first: bool | None = None
    cloud_permitted: bool | None = None
    allowed_capabilities: list[str] | None = None
    custom_settings: dict[str, Any] | None = None


class AgentStatusResponse(BaseModel):
    """Live runtime status report for an agent."""

    agent_id: str
    name: str
    category: AgentCategory
    availability_state: AvailabilityState
    enabled: bool
    active_assignments: int
    concurrency_limit: int
    is_busy: bool
    preferred_model: str | None
    total_executions: int = 0
    successful_executions: int = 0
    failed_executions: int = 0
    last_execution_at: datetime | None = None
