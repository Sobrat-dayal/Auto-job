"""Stage 20: Workflow Reliability, Action Recording, Procedure Schema & Recovery Contracts."""

from datetime import datetime, timezone
from enum import Enum
import hashlib
import json
from typing import Any, Dict, List, Optional
import uuid

from pydantic import BaseModel, Field


# =============================================================================
# Enums
# =============================================================================

class RecordingMode(str, Enum):
    """Execution context and trigger for recording."""
    AUTOMATIC_AUTHORIZED = "AUTOMATIC_AUTHORIZED"
    USER_INITIATED = "USER_INITIATED"
    WORKFLOW_EXECUTION = "WORKFLOW_EXECUTION"
    DIAGNOSTIC = "DIAGNOSTIC"


class RecordingStatus(str, Enum):
    """Lifecycle states of an action recording session."""
    CREATED = "created"
    CONFIGURED = "configured"
    RECORDING = "recording"
    ACTIVE = "active"
    PAUSED = "paused"
    FINALIZING = "finalizing"
    COMPLETED = "completed"
    STOPPED = "stopped"
    SEALED = "sealed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ProcedureValidationStatus(str, Enum):
    """Lifecycle and safety certification status of a reusable procedure."""
    DRAFT = "draft"
    VALIDATING = "validating"
    VALIDATED = "validated"
    VALID = "validated"
    WARNING = "warning"
    INVALID = "invalid"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    DISABLED = "disabled"


class SideEffectClass(str, Enum):
    """Idempotency and side-effect impact classification of a procedure step."""
    READ_ONLY = "READ_ONLY"
    IDEMPOTENT = "IDEMPOTENT"
    CONDITIONALLY_IDEMPOTENT = "CONDITIONALLY_IDEMPOTENT"
    NON_IDEMPOTENT = "NON_IDEMPOTENT"
    IRREVERSIBLE = "IRREVERSIBLE"


class CheckpointPolicy(str, Enum):
    """Rule determining when checkpoints are automatically committed."""
    NONE = "none"
    STEP = "step"
    BEFORE_IRREVERSIBLE = "before_irreversible"
    AFTER_IRREVERSIBLE = "after_irreversible"
    ON_FAILURE = "on_failure"


class ReplayMode(str, Enum):
    """Execution modality for procedure replay."""
    DRY_RUN = "dry_run"
    STEP_BY_STEP = "step_by_step"
    AUTOMATIC_AUTHORIZED = "automatic_authorized"
    RESUME_FROM_CHECKPOINT = "resume_from_checkpoint"


class ProcedureExecutionStatus(str, Enum):
    """Lifecycle states of a procedure execution run."""
    PENDING = "pending"
    PREFLIGHT = "preflight"
    RUNNING = "running"
    PAUSED = "paused"
    WAITING_USER_INPUT = "waiting_user_input"
    WAITING_APPROVAL = "waiting_approval"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class CheckpointType(str, Enum):
    """Granularity and intent of a persistent checkpoint."""
    STEP = "step"
    POST_ACTION = "step"
    PRE_ACTION = "step"
    PRE_SIDE_EFFECT = "milestone"
    PERIODIC = "milestone"
    MILESTONE = "milestone"
    ARTIFACT = "artifact"
    APPLICATION_STATE = "application_state"
    RECOVERY = "recovery"


class SideEffectOutcome(str, Enum):
    """Verification and reconciliation status of an external side-effect."""
    PENDING = "dispatched"
    DISPATCHED = "dispatched"
    CONFIRMED = "confirmed"
    DENIED = "denied"
    DUPLICATE_BLOCKED = "duplicate_blocked"
    INDETERMINATE = "indeterminate"
    UNKNOWN_OUTCOME = "unknown_outcome"
    RECONCILED = "reconciled"
    FAILED = "failed"


class RecoveryClassification(str, Enum):
    """Taxonomy of crash and interruption recovery viability."""
    SAFE_TO_RESUME = "safe_to_resume"
    SAFE_TO_RETRY = "safe_to_resume"
    SKIP_AND_CONTINUE = "skip_and_continue"
    REQUIRES_REPLAN = "requires_replan"
    UNRECOVERABLE = "unrecoverable"
    REQUIRES_REOBSERVATION = "requires_reobservation"
    REQUIRES_REAUTHENTICATION = "requires_reauthentication"
    REQUIRES_RESOURCE_RESTORATION = "requires_resource_restoration"
    REQUIRES_AUTHORIZATION = "requires_authorization"
    REQUIRES_USER_INPUT = "requires_user_input"
    EXTERNAL_OUTCOME_UNKNOWN = "external_outcome_unknown"
    NONRECOVERABLE = "nonrecoverable"
    CANCELLED = "cancelled"


# =============================================================================
# Action Recording Contracts
# =============================================================================

class RecordedAction(BaseModel):
    """A single normalized, privacy-filtered computer action captured during execution."""
    action_id: str = Field(default_factory=lambda: f"rec_act_{uuid.uuid4().hex[:12]}")
    sequence_index: int = 0
    session_id: str
    source_adapter: str  # BROWSER_DOM, WINDOWS_UIA, WINDOWS_WIN32, VISUAL_GROUNDING
    capability_id: str = "hybrid_execute"
    workflow_id: Optional[str] = None
    task_id: Optional[str] = None
    agent_id: Optional[str] = "windows_computer_agent"

    target_type: str = "unknown"
    target_summary: str = ""
    target_identity: Dict[str, Any] = Field(default_factory=dict)
    action_type: str  # click, enter_text, navigate, scroll, submit, etc.
    approved_parameters: Dict[str, Any] = Field(default_factory=dict)

    preconditions: List[Dict[str, Any]] = Field(default_factory=list)
    postconditions: List[Dict[str, Any]] = Field(default_factory=list)

    execution_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    result_status: str = "success"  # success, failed
    verification_outcome: str = "success"  # success, failed, unknown_outcome, not_verified
    execution_time_ms: float = 0.0
    error_message: Optional[str] = None

    routing_metadata: Dict[str, Any] = Field(default_factory=dict)
    evidence_refs: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)

    # Convenience aliases and compatibility properties
    sequence_number: int = 0
    normalized_parameters: Dict[str, Any] = Field(default_factory=dict)
    raw_parameters: Dict[str, Any] = Field(default_factory=dict)
    is_sensitive: bool = False
    application_name: Optional[str] = None
    window_title: Optional[str] = None
    web_origin: Optional[str] = None
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if self.sequence_number == 0 and self.sequence_index >= 0:
            self.sequence_number = self.sequence_index + 1
        elif self.sequence_index == 0 and self.sequence_number > 0:
            self.sequence_index = self.sequence_number - 1

        if self.approved_parameters and not self.normalized_parameters:
            self.normalized_parameters = dict(self.approved_parameters)
        elif self.normalized_parameters and not self.approved_parameters:
            self.approved_parameters = dict(self.normalized_parameters)

        if not self.application_name and self.target_identity:
            self.application_name = self.target_identity.get("process_name")
        if not self.window_title and self.target_identity:
            self.window_title = self.target_identity.get("window_title")
        if not self.web_origin and self.target_identity:
            self.web_origin = self.target_identity.get("url") or self.target_identity.get("origin")

        if any("[REDACTED" in str(v) for v in self.normalized_parameters.values()):
            self.is_sensitive = True


class RecordingSession(BaseModel):
    """An active or finalized computer interaction recording session."""
    session_id: str = Field(default_factory=lambda: f"recsess_{uuid.uuid4().hex[:12]}")
    name: str = "Recording Session"
    owner_id: str = "user"
    mode: RecordingMode = RecordingMode.USER_INITIATED
    status: RecordingStatus = RecordingStatus.CREATED
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None

    allowed_app_scopes: List[str] = Field(default_factory=list)  # e.g. ["chrome.exe", "notepad.exe"]
    allowed_web_origins: List[str] = Field(default_factory=list)  # e.g. ["https://localtest.domain"]

    captured_actions_count: int = 0
    excluded_events_count: int = 0
    integrity_hash: Optional[str] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    finalized_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class StartRecordingRequest(BaseModel):
    """Request payload to initiate a structured recording session."""
    name: Optional[str] = "Interactive Procedure Recording"
    mode: RecordingMode = RecordingMode.USER_INITIATED
    workflow_id: Optional[str] = None
    agent_id: Optional[str] = None
    allowed_app_scopes: List[str] = Field(default_factory=list)
    allowed_web_origins: List[str] = Field(default_factory=list)
    metadata: Dict[str, Any] = Field(default_factory=dict)


# =============================================================================
# Procedure Schema & Definition Contracts
# =============================================================================

class ProcedureParameter(BaseModel):
    """A parameterized input contract for reusable procedures."""
    name: str
    type: str = "string"  # string, number, boolean, filepath, url
    required: bool = True
    default_value: Optional[Any] = None
    description: str = ""
    sensitivity: str = "PUBLIC"  # PUBLIC, PROTECTED, SECRET


class ProcedureStep(BaseModel):
    """A single declarative, repeatable step within a compiled procedure."""
    step_id: str = Field(default_factory=lambda: f"step_{uuid.uuid4().hex[:8]}")
    sequence_index: int = 0
    order_index: int = 0
    name: str = ""
    target_surface: str = "hybrid"
    locator_schema: Dict[str, Any] = Field(default_factory=dict)
    capability_id: str = "hybrid_execute"
    preferred_method: Optional[str] = None  # None = dynamic auto-route

    target: Dict[str, Any] = Field(default_factory=dict)
    input_bindings: Dict[str, Any] = Field(default_factory=dict)
    action_type: str = "click"

    preconditions: List[Dict[str, Any]] = Field(default_factory=list)
    postconditions: List[Dict[str, Any]] = Field(default_factory=list)

    timeout_seconds: int = 15
    timeout_ms: int = 15000
    max_retries: int = 2
    allow_failure: bool = False
    retry_policy: Dict[str, Any] = Field(
        default_factory=lambda: {"max_retries": 2, "backoff_ms": 500, "allow_fallback": True}
    )
    side_effect_class: SideEffectClass = SideEffectClass.REPEATABLE if hasattr(SideEffectClass, "REPEATABLE") else SideEffectClass.IDEMPOTENT
    checkpoint_policy: CheckpointPolicy = CheckpointPolicy.NONE
    description: str = ""

    def model_post_init(self, __context: Any) -> None:
        if self.order_index == 0 and self.sequence_index >= 0:
            self.order_index = self.sequence_index + 1
        elif self.sequence_index == 0 and self.order_index > 0:
            self.sequence_index = self.order_index - 1

        if self.locator_schema and not self.target:
            self.target = dict(self.locator_schema)
        elif self.target and not self.locator_schema:
            self.locator_schema = dict(self.target)

        if not self.name:
            self.name = self.description or f"Step {self.order_index}: {self.action_type}"
        elif not self.description:
            self.description = self.name


class ReusableProcedure(BaseModel):
    """An immutable, versioned, declarative multi-application procedure."""
    procedure_id: str = Field(default_factory=lambda: f"proc_{uuid.uuid4().hex[:12]}")
    version: int = 1
    name: str
    description: str = ""
    category: str = "general"

    parameters: List[ProcedureParameter] = Field(default_factory=list)
    required_permissions: List[str] = Field(default_factory=list)
    steps: List[ProcedureStep] = Field(default_factory=list)

    compatibility: Dict[str, Any] = Field(
        default_factory=lambda: {
            "required_capabilities": ["hybrid_execute"],
            "min_adapter_version": "1.0.0",
            "supported_apps": [],
        }
    )
    risk_assessment: Dict[str, Any] = Field(
        default_factory=lambda: {
            "risk_level": "LOW",
            "destructive_ops": [],
            "external_transmissions": [],
            "irreversible_steps": [],
        }
    )
    validation_status: ProcedureValidationStatus = ProcedureValidationStatus.DRAFT
    checksum: Optional[str] = None

    is_draft: bool = True
    is_deprecated: bool = False
    author: Optional[str] = None
    allowed_applications: List[str] = Field(default_factory=list)
    allowed_origins: List[str] = Field(default_factory=list)
    validation_issues: List[str] = Field(default_factory=list)
    static_risk_score: int = 0
    originating_session_id: Optional[str] = None

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def calculate_checksum(self) -> str:
        """Calculate SHA-256 fingerprint over structural step definition."""
        norm_steps = [
            {
                "step_id": s.step_id,
                "action_type": s.action_type,
                "target": s.target,
                "input_bindings": s.input_bindings,
                "side_effect_class": s.side_effect_class.value,
            }
            for s in self.steps
        ]
        payload = json.dumps(
            {"id": self.procedure_id, "ver": self.version, "steps": norm_steps},
            sort_keys=True,
        )
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()


class CompileProcedureRequest(BaseModel):
    """Request payload to transform a recording session into a reusable procedure."""
    session_id: str
    name: str
    description: Optional[str] = ""
    category: Optional[str] = "general"
    parameterize_inputs: bool = True


# =============================================================================
# Replay, Checkpoint & Side-Effect Contracts
# =============================================================================

class PreflightReport(BaseModel):
    """Validation report generated prior to executing or resuming a procedure."""
    is_eligible: bool = True
    can_execute: bool = True
    procedure_id: str
    version: int
    mode: ReplayMode = ReplayMode.AUTOMATIC_AUTHORIZED

    parameter_checks: Dict[str, bool] = Field(default_factory=dict)
    capability_checks: Dict[str, bool] = Field(default_factory=dict)
    adapter_checks: Dict[str, bool] = Field(default_factory=dict)
    permission_checks: Dict[str, bool] = Field(default_factory=dict)
    session_check: bool = True
    emergency_stop_check: bool = True

    # Compatibility fields for tests and frontend
    missing_parameters: List[str] = Field(default_factory=list)
    missing_permissions: List[str] = Field(default_factory=list)
    required_adapters: List[str] = Field(default_factory=list)
    adapters_ready: bool = True
    emergency_stop_active: bool = False
    session_locked: bool = False
    risk_assessment: Dict[str, Any] = Field(default_factory=dict)

    external_side_effects: List[str] = Field(default_factory=list)
    issues: List[str] = Field(default_factory=list)
    recommendation: str = "Ready for execution"

    def model_post_init(self, __context: Any) -> None:
        if not self.is_eligible and self.can_execute:
            self.can_execute = False
        elif not self.can_execute and self.is_eligible:
            self.is_eligible = False
    recommendation: str = "Ready for execution"


class StateFingerprint(BaseModel):
    """Bounded, privacy-safe application and system state snapshot."""
    fingerprint_id: str = Field(default_factory=lambda: f"fp_{uuid.uuid4().hex[:12]}")
    browser_state: Optional[Dict[str, Any]] = None  # origin, page_title, url
    native_state: Optional[Dict[str, Any]] = None   # window_title, process_name, hwnd
    visual_state: Optional[Dict[str, Any]] = None   # frame_hash, screen_res
    artifact_state: Optional[Dict[str, Any]] = None # path, sha256, size_bytes
    active_window_title: Optional[str] = None
    active_process_name: Optional[str] = None
    browser_url: Optional[str] = None
    extra_attributes: Dict[str, Any] = Field(default_factory=dict)
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if self.native_state:
            if not self.active_window_title:
                self.active_window_title = self.native_state.get("window_title")
            if not self.active_process_name:
                self.active_process_name = self.native_state.get("process_name")
        elif self.active_window_title or self.active_process_name:
            self.native_state = {
                "window_title": self.active_window_title or "",
                "process_name": self.active_process_name or "",
            }

        if self.browser_state:
            if not self.browser_url:
                self.browser_url = self.browser_state.get("origin") or self.browser_state.get("url")
        elif self.browser_url:
            self.browser_state = {"origin": self.browser_url, "url": self.browser_url}


class ExecutionCheckpoint(BaseModel):
    """Durable milestone capturing verifiable progress and restoration metadata."""
    checkpoint_id: str = Field(default_factory=lambda: f"chk_{uuid.uuid4().hex[:12]}")
    execution_id: str
    procedure_id: str = "default_proc"
    procedure_version: int = 1
    step_id: Optional[str] = None
    step_index: int = 0
    checkpoint_type: CheckpointType = CheckpointType.STEP

    completed_step_ids: List[str] = Field(default_factory=list)
    completed_steps: List[str] = Field(default_factory=list)
    verified_outputs: Dict[str, Any] = Field(default_factory=dict)
    artifact_refs: List[str] = Field(default_factory=list)
    fingerprint: StateFingerprint = Field(default_factory=StateFingerprint)
    state_fingerprint: Optional[StateFingerprint] = None
    scope_variables: Dict[str, Any] = Field(default_factory=dict)
    pending_step_ids: List[str] = Field(default_factory=list)
    side_effect_ledger_ids: List[str] = Field(default_factory=list)

    integrity_hash: str = ""
    can_resume: bool = True
    is_valid: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if self.completed_steps and not self.completed_step_ids:
            self.completed_step_ids = list(self.completed_steps)
        elif self.completed_step_ids and not self.completed_steps:
            self.completed_steps = list(self.completed_step_ids)

        if self.state_fingerprint and not self.fingerprint.browser_state and not self.fingerprint.native_state:
            self.fingerprint = self.state_fingerprint
        elif not self.state_fingerprint:
            self.state_fingerprint = self.fingerprint

        if not self.integrity_hash:
            self.integrity_hash = self.compute_integrity()

    def compute_integrity(self) -> str:
        """Compute SHA-256 over checkpoint properties."""
        content = f"{self.checkpoint_id}:{self.execution_id}:{self.step_index}:{','.join(self.completed_step_ids)}"
        return hashlib.sha256(content.encode("utf-8")).hexdigest()


class ExternalSideEffect(BaseModel):
    """Durable ledger record of consequential external state mutation."""
    effect_id: str = Field(default_factory=lambda: f"eff_{uuid.uuid4().hex[:12]}")
    execution_id: str
    step_id: str
    intent_id: str = ""
    idempotency_key: Optional[str] = None
    action_category: str = "general"
    destination: str = ""
    parameter_digest: str = ""
    outcome: SideEffectOutcome = SideEffectOutcome.DISPATCHED
    evidence: Dict[str, Any] = Field(default_factory=dict)
    dispatched_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    reconciled_at: Optional[datetime] = None

    # Convenience aliases
    target_system: Optional[str] = None
    operation: Optional[str] = None
    parameters: Dict[str, Any] = Field(default_factory=dict)
    intent_hash: Optional[str] = None
    side_effect_class: SideEffectClass = SideEffectClass.NON_IDEMPOTENT

    def model_post_init(self, __context: Any) -> None:
        if self.target_system and not self.destination:
            self.destination = self.target_system
        elif self.destination and not self.target_system:
            self.target_system = self.destination

        if self.operation and not self.action_category:
            self.action_category = self.operation
        elif self.action_category and not self.operation:
            self.operation = self.action_category

        if self.intent_hash and not self.intent_id:
            self.intent_id = self.intent_hash
        elif self.intent_id and not self.intent_hash:
            self.intent_hash = self.intent_id


class ProcedureExecution(BaseModel):
    """Live state record of an active or completed procedure execution run."""
    execution_id: str = Field(default_factory=lambda: f"procexec_{uuid.uuid4().hex[:12]}")
    procedure_id: str
    version: int
    mode: ReplayMode = ReplayMode.AUTOMATIC_AUTHORIZED
    status: ProcedureExecutionStatus = ProcedureExecutionStatus.PENDING

    parameters: Dict[str, Any] = Field(default_factory=dict)
    resolved_arguments: Dict[str, Any] = Field(default_factory=dict)
    current_step_index: int = 0
    total_steps: int = 0
    completed_steps: List[str] = Field(default_factory=list)
    failed_steps: List[str] = Field(default_factory=list)
    latest_checkpoint_id: Optional[str] = None
    checkpoints: List[ExecutionCheckpoint] = Field(default_factory=list)
    side_effects: List[ExternalSideEffect] = Field(default_factory=list)
    side_effect_count: int = 0
    error_message: Optional[str] = None

    started_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
    execution_time_ms: float = 0.0

    def model_post_init(self, __context: Any) -> None:
        if self.parameters and not self.resolved_arguments:
            self.resolved_arguments = dict(self.parameters)
        elif self.resolved_arguments and not self.parameters:
            self.parameters = dict(self.resolved_arguments)


class RecoveryPlan(BaseModel):
    """Structured plan for safe, non-duplicative workflow continuation."""
    plan_id: str = Field(default_factory=lambda: f"recplan_{uuid.uuid4().hex[:12]}")
    execution_id: str
    checkpoint_id: str
    classification: RecoveryClassification
    can_resume: bool

    steps_to_skip: List[str] = Field(default_factory=list)
    steps_to_revalidate: List[str] = Field(default_factory=list)
    steps_to_execute: List[str] = Field(default_factory=list)
    actions_to_skip: List[str] = Field(default_factory=list)
    actions_to_reexecute: List[str] = Field(default_factory=list)
    resume_step_index: int = 0
    rationale: str = ""
    uncertain_operations: List[Dict[str, Any]] = Field(default_factory=list)
    required_permissions: List[str] = Field(default_factory=list)
    explanation: str = ""
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    def model_post_init(self, __context: Any) -> None:
        if self.steps_to_skip and not self.actions_to_skip:
            self.actions_to_skip = list(self.steps_to_skip)
        elif self.actions_to_skip and not self.steps_to_skip:
            self.steps_to_skip = list(self.actions_to_skip)

        if self.steps_to_execute and not self.actions_to_reexecute:
            self.actions_to_reexecute = list(self.steps_to_execute)
        elif self.actions_to_reexecute and not self.steps_to_execute:
            self.steps_to_execute = list(self.actions_to_reexecute)

        if self.explanation and not self.rationale:
            self.rationale = self.explanation
        elif self.rationale and not self.explanation:
            self.explanation = self.rationale


class ReliabilityDiagnosticsInfo(BaseModel):
    """High-level system health and reliability telemetry."""
    service_status: str = "operational"
    active_recordings: int = 0
    active_recording_sessions: int = 0
    total_procedures: int = 0
    total_registered_procedures: int = 0
    published_procedures: int = 0
    active_executions: int = 0
    pending_recoveries: int = 0
    interrupted_executions_found: int = 0
    total_checkpoints: int = 0
    total_checkpoints_preserved: int = 0
    total_side_effects: int = 0
    tracked_side_effects_count: int = 0
    emergency_stop_active: bool = False
    emergency_stop_triggered: bool = False
    is_session_locked: bool = False

    def model_post_init(self, __context: Any) -> None:
        if self.active_recordings and not self.active_recording_sessions:
            self.active_recording_sessions = self.active_recordings
        elif self.active_recording_sessions and not self.active_recordings:
            self.active_recordings = self.active_recording_sessions

        if self.total_procedures and not self.total_registered_procedures:
            self.total_registered_procedures = self.total_procedures
        elif self.total_registered_procedures and not self.total_procedures:
            self.total_procedures = self.total_registered_procedures

        if self.total_checkpoints and not self.total_checkpoints_preserved:
            self.total_checkpoints_preserved = self.total_checkpoints
        elif self.total_checkpoints_preserved and not self.total_checkpoints:
            self.total_checkpoints = self.total_checkpoints_preserved

        if self.total_side_effects and not self.tracked_side_effects_count:
            self.tracked_side_effects_count = self.total_side_effects
        elif self.tracked_side_effects_count and not self.total_side_effects:
            self.total_side_effects = self.tracked_side_effects_count

        if self.emergency_stop_active and not self.emergency_stop_triggered:
            self.emergency_stop_triggered = self.emergency_stop_active
        elif self.emergency_stop_triggered and not self.emergency_stop_active:
            self.emergency_stop_active = self.emergency_stop_triggered
