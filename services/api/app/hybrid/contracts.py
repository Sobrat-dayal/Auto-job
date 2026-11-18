"""Data contracts and schemas for the Stage 19 Hybrid Computer Interaction Engine."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional
import uuid

from pydantic import BaseModel, Field, model_validator


def utc_now() -> datetime:
    """Return timezone-aware UTC datetime."""
    return datetime.now(timezone.utc)


class InteractionMethod(str, Enum):
    """Interaction methods available for computer control."""
    BROWSER_DOM = "BROWSER_DOM"
    WINDOWS_UIA = "WINDOWS_UIA"
    WINDOWS_WIN32 = "WINDOWS_WIN32"
    VISUAL_GROUNDING = "VISUAL_GROUNDING"


class SurfaceType(str, Enum):
    """Classified surface type for an interaction target."""
    BROWSER_DOM = "BROWSER_DOM"
    NATIVE_UIA = "NATIVE_UIA"
    NATIVE_WIN32 = "NATIVE_WIN32"
    CUSTOM_RENDERED = "CUSTOM_RENDERED"
    EMBEDDED_WEBVIEW = "EMBEDDED_WEBVIEW"
    UNKNOWN = "UNKNOWN"


class TargetType(str, Enum):
    """Classification of target entities."""
    BROWSER_PAGE = "BROWSER_PAGE"
    BROWSER_TAB = "BROWSER_TAB"
    BROWSER_FRAME = "BROWSER_FRAME"
    BROWSER_ELEMENT = "BROWSER_ELEMENT"
    NATIVE_APP = "NATIVE_APP"
    NATIVE_WINDOW = "NATIVE_WINDOW"
    UIA_ELEMENT = "UIA_ELEMENT"
    VISUAL_CAPTURE_TARGET = "VISUAL_CAPTURE_TARGET"
    VISUAL_REGION = "VISUAL_REGION"


class ActionRiskLevel(str, Enum):
    """Risk and idempotency level for interaction actions."""
    READ_ONLY = "READ_ONLY"
    REPEATABLE = "REPEATABLE"
    CONDITIONALLY_REPEATABLE = "CONDITIONALLY_REPEATABLE"
    NON_IDEMPOTENT = "NON_IDEMPOTENT"
    IRREVERSIBLE = "IRREVERSIBLE"


class HybridActionType(str, Enum):
    """Unified action types across all interaction methods."""
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    ENTER_TEXT = "enter_text"
    NAVIGATE = "navigate"
    SCROLL = "scroll"
    KEY_PRESS = "key_press"
    HOTKEY = "hotkey"
    INSPECT = "inspect"
    SUBMIT = "submit"
    SELECT_OPTION = "select_option"


class HybridTaskStatus(str, Enum):
    """Lifecycle status for a hybrid execution task."""
    PENDING = "pending"
    ROUTING = "routing"
    EXECUTING = "executing"
    VERIFYING = "verifying"
    FALLING_BACK = "falling_back"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    BLOCKED_POLICY = "blocked_policy"
    WAITING_APPROVAL = "waiting_approval"


class HybridVerificationStatus(str, Enum):
    """Status resulting from post-action verification."""
    SUCCESS = "success"
    FAILED = "failed"
    UNKNOWN_OUTCOME = "unknown_outcome"
    NOT_VERIFIED = "not_verified"


class InteractionTarget(BaseModel):
    """Unified target identity spanning browser, native UIA, Win32, and visual surfaces."""
    target_id: str = Field(default_factory=lambda: f"tgt_{uuid.uuid4().hex[:12]}")
    target_type: TargetType
    surface_type: SurfaceType = SurfaceType.UNKNOWN

    # Browser references
    session_id: Optional[str] = None
    browser_context_id: Optional[str] = None
    page_id: Optional[str] = None
    dom_selector: Optional[str] = None

    # Native Windows & UIA references
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    window_handle: Optional[int] = None
    window_ref: Optional[str] = None
    uia_runtime_id: Optional[str] = None
    control_type: Optional[str] = None
    element_name: Optional[str] = None

    # Visual references
    visual_target_name: Optional[str] = None
    coordinates: Optional[dict[str, Any]] = None
    bounds: Optional[dict[str, Any]] = None

    # Security & observation provenance
    authorization_scope: str = "*"
    last_observed_at: Optional[datetime] = None
    metadata: dict[str, Any] = Field(default_factory=dict)

    @model_validator(mode="before")
    @classmethod
    def remap_target_fields(cls, values: Any) -> Any:
        if isinstance(values, dict):
            if "hwnd" in values and "window_handle" not in values:
                values["window_handle"] = values["hwnd"]
            if "pid" in values and "process_id" not in values:
                values["process_id"] = values["pid"]
        return values


class CapabilityProbe(BaseModel):
    """Method-specific capability probe result for a given target."""
    method: InteractionMethod
    is_available: bool = True
    is_applicable: bool = True
    confidence_score: float = 1.0
    supported_actions: list[str] = Field(default_factory=list)
    required_permissions: list[str] = Field(default_factory=list)
    resource_cost_score: int = 1  # 1 (low: DOM) to 5 (high: vision model)
    latency_ms_estimate: int = 20
    verification_supported: bool = True
    reason: str = ""
    probed_at: datetime = Field(default_factory=utc_now)


class ObservationRequest(BaseModel):
    """Request to observe a target using an appropriate or preferred method."""
    target: InteractionTarget
    preferred_method: Optional[InteractionMethod] = None
    include_snapshot: bool = True
    include_visual: bool = False
    timeout_ms: int = 5000


class InteractionObservation(BaseModel):
    """Normalized cross-method observation result."""
    observation_id: str = Field(default_factory=lambda: f"obs_{uuid.uuid4().hex[:12]}")
    target_id: str
    method: InteractionMethod
    surface_type: SurfaceType
    observed_text: Optional[str] = None
    structure_summary: Optional[str] = None
    dom_elements: list[dict[str, Any]] = Field(default_factory=list)
    uia_elements: list[dict[str, Any]] = Field(default_factory=list)
    visual_detections: list[dict[str, Any]] = Field(default_factory=list)
    is_valid: bool = True
    is_stale: bool = False
    captured_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class InteractionAction(BaseModel):
    """Unified action instruction across all interaction methods."""
    action_id: str = Field(default_factory=lambda: f"act_{uuid.uuid4().hex[:12]}")
    task_id: Optional[str] = None
    target: InteractionTarget
    action_type: HybridActionType
    method: Optional[InteractionMethod] = None  # None = let router decide
    input_text: Optional[str] = None
    key: Optional[str] = None
    hotkey_modifiers: list[str] = Field(default_factory=list)
    url: Optional[str] = None
    click_offset: Optional[dict[str, int]] = None
    risk_level: ActionRiskLevel = ActionRiskLevel.REPEATABLE
    is_non_idempotent: bool = False
    expected_mutation: Optional[str] = None
    timeout_ms: int = 10000
    allow_fallback: bool = True
    metadata: dict[str, Any] = Field(default_factory=dict)


class InteractionResult(BaseModel):
    """Outcome of an interaction action execution."""
    action_id: str
    method: InteractionMethod
    success: bool
    execution_time_ms: float = 0.0
    verification_status: HybridVerificationStatus = HybridVerificationStatus.NOT_VERIFIED
    verification_details: str = ""
    error_message: Optional[str] = None
    mutation_detected: bool = False
    fallback_occurred: bool = False
    fallback_attempts: int = 0
    executed_at: datetime = Field(default_factory=utc_now)
    metadata: dict[str, Any] = Field(default_factory=dict)


class RoutingDecisionRecordSchema(BaseModel):
    """Explainable audit record of a method routing choice."""
    decision_id: str = Field(default_factory=lambda: f"dec_{uuid.uuid4().hex[:12]}")
    task_id: Optional[str] = None
    target_id: str
    selected_method: InteractionMethod
    candidate_methods: list[InteractionMethod] = Field(default_factory=list)
    rejected_methods: dict[str, str] = Field(default_factory=dict)
    scoring: dict[str, float] = Field(default_factory=dict)
    rationale: str
    decided_at: datetime = Field(default_factory=utc_now)


class FallbackRecordSchema(BaseModel):
    """Audit record of a context-aware fallback event."""
    fallback_id: str = Field(default_factory=lambda: f"fb_{uuid.uuid4().hex[:12]}")
    task_id: str
    initial_method: InteractionMethod
    fallback_method: InteractionMethod
    trigger_reason: str
    reobservation_successful: bool = True
    outcome: str = "success"
    timestamp: datetime = Field(default_factory=utc_now)


class HybridTaskRequest(BaseModel):
    """Operator or supervisor instruction to run a hybrid computer task."""
    instruction: str
    target: Optional[InteractionTarget] = None
    action_type: Optional[HybridActionType] = None
    preferred_method: Optional[InteractionMethod] = None
    allow_fallback: bool = True
    max_fallback_steps: int = 3
    require_verification: bool = True
    context: dict[str, Any] = Field(default_factory=dict)


class HybridTaskResponse(BaseModel):
    """Status and result response for a hybrid task."""
    task_id: str
    status: HybridTaskStatus
    instruction: str
    selected_method: Optional[InteractionMethod] = None
    routing_decision: Optional[RoutingDecisionRecordSchema] = None
    attempts: list[dict[str, Any]] = Field(default_factory=list)
    final_result: Optional[InteractionResult] = None
    error_message: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


class MethodHealthStatus(BaseModel):
    """Operational health telemetry for an interaction method."""
    method: InteractionMethod
    status: str = "operational"  # operational, degraded, unavailable
    success_count: int = 0
    failure_count: int = 0
    avg_latency_ms: float = 0.0
    last_error: Optional[str] = None
    last_used_at: Optional[datetime] = None


class HybridDiagnosticsInfo(BaseModel):
    """Consolidated diagnostic report of the Hybrid Computer Interaction Engine."""
    engine_version: str = "1.0.0"
    is_healthy: bool = True
    emergency_stop_active: bool = False
    input_lease_owner: Optional[str] = None
    methods: list[MethodHealthStatus] = Field(default_factory=list)
    total_tasks: int = 0
    active_tasks: int = 0
    total_fallbacks: int = 0
    recent_routing_decisions: list[RoutingDecisionRecordSchema] = Field(default_factory=list)
