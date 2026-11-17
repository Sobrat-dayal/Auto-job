"""Contracts, data models, and enums for the centralized AUTONOM Authorization Engine (Stage 14)."""

from datetime import UTC, datetime
from enum import Enum
import hashlib
import json
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field


class RiskLevel(str, Enum):
    """Categorized risk classification for actions."""

    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"

    @property
    def level_order(self) -> int:
        order_map = {"low": 1, "moderate": 2, "high": 3, "critical": 4}
        return order_map[self.value]


class PermissionCategory(str, Enum):
    """Centralized permission taxonomy."""

    READ = "read"
    WRITE = "write"
    DESTRUCTIVE = "destructive"
    EXTERNAL = "external"
    COMPUTER_CONTROL = "computer_control"
    AI_INTEGRATION = "ai_integration"


class ActionEffect(str, Enum):
    """Deterministic authorization decision outcomes."""

    ALLOW = "allow"
    DENY = "deny"
    REQUIRE_APPROVAL = "require_approval"


class ApprovalStatus(str, Enum):
    """Lifecycle states of an approval request."""

    PENDING = "pending"
    APPROVED = "approved"
    DENIED = "denied"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    REVOKED = "revoked"
    CONSUMED = "consumed"


class ApprovalMode(str, Enum):
    """Scope of an approval decision."""

    ONE_TIME = "one_time"
    TASK_SCOPED = "task_scoped"
    WORKFLOW_SCOPED = "workflow_scoped"
    STANDING = "standing"


class GrantType(str, Enum):
    """Preauthorized autonomy grant categories."""

    STANDING = "standing"
    WORKFLOW_SCOPED = "workflow_scoped"
    TASK_SCOPED = "task_scoped"
    TIME_LIMITED = "time_limited"
    ONE_TIME = "one_time"


class ReasonCode(str, Enum):
    """Machine-readable reason codes for authorization decisions."""

    EMERGENCY_STOP_ACTIVE = "EMERGENCY_STOP_ACTIVE"
    AUTOMATION_PAUSED = "AUTOMATION_PAUSED"
    CREDENTIAL_ACCESS_RESTRICTED = "CREDENTIAL_ACCESS_RESTRICTED"
    EXPLICIT_DENY_POLICY = "EXPLICIT_DENY_POLICY"
    PREAUTHORIZED_GRANT = "PREAUTHORIZED_GRANT"
    EXPLICIT_ALLOW_POLICY = "EXPLICIT_ALLOW_POLICY"
    APPROVAL_REQUIRED_BY_POLICY = "APPROVAL_REQUIRED_BY_POLICY"
    APPROVAL_GRANTED = "APPROVAL_GRANTED"
    HIGH_RISK_ACTION = "HIGH_RISK_ACTION"
    READ_ONLY_BASELINE = "READ_ONLY_BASELINE"
    RESOURCE_OUT_OF_SCOPE = "RESOURCE_OUT_OF_SCOPE"
    GRANT_EXPIRED = "GRANT_EXPIRED"
    GRANT_REVOKED = "GRANT_REVOKED"
    GRANT_USAGE_EXCEEDED = "GRANT_USAGE_EXCEEDED"
    DEFAULT_DENY = "DEFAULT_DENY"


class ActorContext(BaseModel):
    """Traceable, authenticated caller identity context."""

    actor_id: str = "user"
    actor_type: str = "user"  # user, supervisor, agent, system
    user_id: str = "default_user"
    agent_id: Optional[str] = None
    workflow_id: Optional[str] = None
    task_id: Optional[str] = None
    step_id: Optional[str] = None
    correlation_id: str = Field(default_factory=lambda: f"corr_{uuid.uuid4().hex[:12]}")


class AuthorizationRequest(BaseModel):
    """Typed evaluation request for any privileged or autonomous operation."""

    actor: ActorContext
    capability_id: str
    action: str
    resource_type: str = "general"
    resource_id: Optional[str] = None
    resource_scope: dict[str, Any] = Field(default_factory=dict)
    parameters: dict[str, Any] = Field(default_factory=dict)
    parameters_digest: Optional[str] = None
    context: dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None

    def compute_digest(self) -> str:
        """Computes deterministic SHA-256 digest of sanitized parameters for replay protection."""
        canonical_json = json.dumps(self.parameters, sort_keys=True, default=str)
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()

    def model_post_init(self, __context: Any) -> None:
        if not self.parameters_digest:
            self.parameters_digest = self.compute_digest()
        if not self.correlation_id:
            self.correlation_id = self.actor.correlation_id


class AuthorizationDecision(BaseModel):
    """Deterministic, auditable decision from the Authorization Engine."""

    decision_id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:12]}")
    outcome: ActionEffect
    policy_id: Optional[str] = None
    grant_id: Optional[str] = None
    reason_code: ReasonCode
    explanation: str
    risk_level: RiskLevel
    expires_at: Optional[datetime] = None
    correlation_id: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_allowed(self) -> bool:
        return self.outcome == ActionEffect.ALLOW

    @property
    def requires_approval(self) -> bool:
        return self.outcome == ActionEffect.REQUIRE_APPROVAL


class PolicyDefinition(BaseModel):
    """Typed, declarative authorization policy."""

    id: str
    name: str
    description: str = ""
    version: int = 1
    is_enabled: bool = True
    is_system: bool = False
    subject_scope: str = "*"  # specific agent_id, 'agent:*', or '*'
    category_scope: str = "*"  # recruitment, coding, etc.
    action_scope: list[str] = Field(default_factory=list)  # capability IDs or actions
    resource_scope: dict[str, Any] = Field(default_factory=dict)
    effect: ActionEffect = ActionEffect.ALLOW
    conditions: dict[str, Any] = Field(default_factory=dict)


class GrantDefinition(BaseModel):
    """Preauthorized autonomy grant."""

    id: str = Field(default_factory=lambda: f"grant_{uuid.uuid4().hex[:10]}")
    name: str
    grant_type: GrantType = GrantType.STANDING
    subject_type: str = "agent"
    subject_id: str = "*"
    workflow_id: Optional[str] = None
    task_id: Optional[str] = None
    allowed_capabilities: list[str] = Field(default_factory=list)
    resource_scope: dict[str, Any] = Field(default_factory=dict)
    risk_limit: RiskLevel = RiskLevel.MODERATE
    valid_from: datetime = Field(default_factory=lambda: datetime.now(UTC))
    valid_until: Optional[datetime] = None
    max_uses: Optional[int] = None
    use_count: int = 0
    is_revoked: bool = False
    revoked_at: Optional[datetime] = None
    revocation_reason: Optional[str] = None
    created_by: str = "user"
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    @property
    def is_active(self) -> bool:
        if self.is_revoked:
            return False
        now = datetime.now(UTC)
        if self.valid_until:
            vu = self.valid_until if self.valid_until.tzinfo is not None else self.valid_until.replace(tzinfo=UTC)
            if vu < now:
                return False
        if self.max_uses is not None and self.use_count >= self.max_uses:
            return False
        return True


class ApprovalRequest(BaseModel):
    """Durable approval request presented to the user."""

    id: str = Field(default_factory=lambda: f"appr_{uuid.uuid4().hex[:10]}")
    workflow_id: Optional[str] = None
    task_id: Optional[str] = None
    step_id: Optional[str] = None
    agent_id: str
    capability_id: str
    action: str
    resource_type: str = "general"
    resource_id: Optional[str] = None
    resource_scope: dict[str, Any] = Field(default_factory=dict)
    parameters_digest: str
    parameters: dict[str, Any] = Field(default_factory=dict)
    reason: str
    risk_level: RiskLevel
    status: ApprovalStatus = ApprovalStatus.PENDING
    approval_mode: ApprovalMode = ApprovalMode.ONE_TIME
    requested_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    expires_at: Optional[datetime] = None
    decided_at: Optional[datetime] = None
    decided_by: Optional[str] = None
    decision_reason: Optional[str] = None
    consumed_at: Optional[datetime] = None


class ApprovalDecisionInput(BaseModel):
    """User resolution payload for an approval request."""

    decision: str = "approve"  # approve or deny
    approval_mode: ApprovalMode = ApprovalMode.ONE_TIME
    reason: Optional[str] = None
    valid_until_seconds: Optional[int] = None


class EmergencyStopState(BaseModel):
    """Authoritative global emergency stop and automation pause telemetry."""

    is_emergency_stop_active: bool = False
    emergency_stop_activated_at: Optional[datetime] = None
    emergency_stop_activated_by: Optional[str] = None
    emergency_stop_reason: Optional[str] = None
    is_automation_paused: bool = False
    automation_paused_at: Optional[datetime] = None
    automation_paused_by: Optional[str] = None
    automation_pause_reason: Optional[str] = None
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
