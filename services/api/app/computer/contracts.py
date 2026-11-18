"""Pydantic data contracts and schemas for Windows Structural Automation (Stage 17)."""

from datetime import UTC, datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class DesktopSessionState(str, Enum):
    ACTIVE = "active"
    LOCKED = "locked"
    DISCONNECTED = "disconnected"
    UNAVAILABLE = "unavailable"


class WindowManageAction(str, Enum):
    ACTIVATE = "activate"
    MINIMIZE = "minimize"
    MAXIMIZE = "maximize"
    RESTORE = "restore"
    CLOSE = "close"


class ControlPatternType(str, Enum):
    INVOKE = "invoke"
    VALUE = "value"
    TOGGLE = "toggle"
    SELECTION = "selection"
    SELECTION_ITEM = "selection_item"
    EXPAND_COLLAPSE = "expand_collapse"
    SCROLL = "scroll"
    TEXT = "text"
    TABLE = "table"
    GRID = "grid"
    WINDOW = "window"
    LEGACY_IA = "legacy_ia"


class DesktopActionType(str, Enum):
    INVOKE = "invoke"
    SET_VALUE = "set_value"
    SELECT = "select"
    TOGGLE = "toggle"
    EXPAND = "expand"
    COLLAPSE = "collapse"
    SCROLL = "scroll"
    READ_TEXT = "read_text"
    ACTIVATE_WINDOW = "activate_window"
    CLOSE_WINDOW = "close_window"
    PRESS_KEY = "press_key"
    GET_WINDOW_STATE = "get_window_state"


class DesktopSessionInfo(BaseModel):
    wts_session_id: int
    status: DesktopSessionState
    desktop_name: str
    user_name: str
    resolution: str
    is_interactive: bool
    is_locked: bool
    last_active_at: datetime


class DesktopApplicationInfo(BaseModel):
    id: str
    name: str
    executable_path: str
    executable_name: str
    publisher: str | None = None
    is_allowed: bool = True
    risk_level: str = "LOW"
    integrity_level: str = "medium"
    pids: list[int] = Field(default_factory=list)
    window_count: int = 0
    last_detected_at: datetime


class WindowBounds(BaseModel):
    left: int
    top: int
    right: int
    bottom: int
    width: int
    height: int


class WindowInfo(BaseModel):
    window_ref: str
    hwnd: int
    pid: int
    process_name: str
    title: str
    window_class: str
    is_visible: bool
    is_enabled: bool
    is_foreground: bool
    is_minimized: bool
    is_maximized: bool
    bounds: WindowBounds
    created_at: datetime
    last_inspected_at: datetime | None = None


class UIElementInfo(BaseModel):
    element_ref: str
    window_ref: str
    name: str | None = None
    automation_id: str | None = None
    control_type: str
    control_type_id: int
    class_name: str | None = None
    framework_id: str | None = None
    is_enabled: bool = True
    is_offscreen: bool = False
    has_keyboard_focus: bool = False
    bounding_box: WindowBounds
    supported_patterns: list[str] = Field(default_factory=list)
    value: str | None = None
    toggle_state: str | None = None
    parent_ref: str | None = None


class UITreeNode(BaseModel):
    element: UIElementInfo
    children: list["UITreeNode"] = Field(default_factory=list)


class InspectionOptions(BaseModel):
    max_depth: int = Field(default=6, ge=1, le=20)
    max_nodes: int = Field(default=250, ge=5, le=1000)
    view_type: str = Field(default="control", pattern="^(control|raw)$")
    timeout_ms: int = Field(default=10000, ge=1000, le=60000)


class UITreeSnapshot(BaseModel):
    window_ref: str
    title: str
    root: UITreeNode
    total_nodes: int
    max_depth_reached: int
    is_truncated: bool
    estimated_tokens: int
    inspected_at: datetime


class ElementQuery(BaseModel):
    automation_id: str | None = None
    name: str | None = None
    control_type: str | None = None
    class_name: str | None = None
    exact_name: bool = False


class DesktopActionRequest(BaseModel):
    action_type: DesktopActionType
    window_ref: str
    element_ref: str | None = None
    locator: ElementQuery | None = None
    value: str | None = None
    key: str | None = None
    modifiers: list[str] = Field(default_factory=list)
    timeout_ms: int = Field(default=15000, ge=1000, le=60000)
    verify: bool = True
    expected_outcome: str | None = None


class DesktopActionResult(BaseModel):
    action_id: str
    action_type: str
    status: str  # succeeded, failed, blocked
    verification_status: str  # verified, failed, unknown, skipped
    duration_ms: float
    result_data: dict[str, Any] = Field(default_factory=dict)
    error_message: str | None = None
    executed_at: datetime


class DesktopTaskRequest(BaseModel):
    goal: str
    target_app: str | None = None
    workflow_id: str | None = None
    step_id: str | None = None


class DesktopTaskResponse(BaseModel):
    task_id: str
    goal: str
    target_app: str | None = None
    status: str
    current_step: int = 0
    total_steps: int = 0
    result: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: datetime
    completed_at: datetime | None = None


class DesktopDiagnosticsInfo(BaseModel):
    session: DesktopSessionInfo
    uia_available: bool
    win32_available: bool
    active_worker_threads: int
    cached_windows: int
    registered_applications: int
    emergency_stop_active: bool
    diagnostic_timestamp: datetime
