"""Data contracts, enums, and schemas for Stage 16 Browser Automation."""

from datetime import datetime
from enum import Enum
from typing import Any
from pydantic import BaseModel, Field


class BrowserType(str, Enum):
    CHROMIUM = "chromium"
    MSEDGE = "msedge"
    CHROME = "chrome"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class BrowserSessionStatus(str, Enum):
    CREATED = "created"
    LAUNCHING = "launching"
    RUNNING = "running"
    PAUSED = "paused"
    ERROR = "error"
    CLOSED = "closed"


class BrowserTabStatus(str, Enum):
    ACTIVE = "active"
    NAVIGATING = "navigating"
    READY = "ready"
    CRASHED = "crashed"
    CLOSED = "closed"


class BrowserActionType(str, Enum):
    NAVIGATE = "navigate"
    CLICK = "click"
    FILL = "fill"
    SELECT = "select"
    CHECK = "check"
    PRESS_KEY = "press_key"
    HOVER = "hover"
    SCROLL = "scroll"
    INSPECT_DOM = "inspect_dom"
    DOWNLOAD = "download"
    SCREENSHOT = "screenshot"
    EVALUATE = "evaluate"


class BrowserActionStatus(str, Enum):
    PENDING = "pending"
    EXECUTING = "executing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    BLOCKED = "blocked"


class BrowserTaskStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class BrowserDownloadStatus(str, Enum):
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


# ---------------------------------------------------------------------------
# Pydantic Schemas
# ---------------------------------------------------------------------------

class BrowserSessionCreateRequest(BaseModel):
    profile_id: str | None = None
    browser_type: BrowserType = BrowserType.CHROMIUM
    channel: str | None = None
    is_headless: bool = True
    viewport_width: int = Field(default=1280, ge=320, le=3840)
    viewport_height: int = Field(default=800, ge=240, le=2160)
    user_agent: str | None = None
    locale: str = "en-US"
    timezone_id: str = "America/New_York"
    metadata: dict[str, Any] = Field(default_factory=dict)


class BrowserTabInfo(BaseModel):
    id: str
    session_id: str
    tab_index: int
    title: str = ""
    url: str = ""
    status: BrowserTabStatus = BrowserTabStatus.READY
    is_active: bool = True
    created_at: datetime
    updated_at: datetime
    closed_at: datetime | None = None


class BrowserSessionResponse(BaseModel):
    id: str
    profile_id: str | None = None
    browser_type: str
    channel: str | None = None
    status: BrowserSessionStatus
    is_headless: bool
    active_tab_id: str | None = None
    pid: int | None = None
    viewport_width: int
    viewport_height: int
    user_agent: str | None = None
    locale: str
    timezone_id: str
    created_at: datetime
    last_activity_at: datetime
    closed_at: datetime | None = None
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
    tabs: list[BrowserTabInfo] = Field(default_factory=list)


class BrowserSessionSummary(BaseModel):
    id: str
    browser_type: str
    channel: str | None = None
    status: BrowserSessionStatus
    is_headless: bool
    active_tab_id: str | None = None
    tab_count: int = 0
    current_url: str = ""
    current_title: str = ""
    created_at: datetime
    last_activity_at: datetime


class BrowserTabCreateRequest(BaseModel):
    url: str | None = None


class BrowserTabSwitchRequest(BaseModel):
    tab_id: str


class BrowserNavigateRequest(BaseModel):
    url: str
    tab_id: str | None = None
    wait_until: str = "domcontentloaded"  # load, domcontentloaded, networkidle
    timeout_ms: int = Field(default=30000, ge=1000, le=120000)


class BrowserNavigateResponse(BaseModel):
    session_id: str
    tab_id: str
    url: str
    title: str
    status_code: int | None = None
    navigation_time_ms: float = 0.0
    is_secure_origin: bool = True


class DOMElementNode(BaseModel):
    id: int
    tag: str
    role: str | None = None
    name: str | None = None
    text: str | None = None
    placeholder: str | None = None
    value: str | None = None
    selector: str
    is_visible: bool = True
    is_enabled: bool = True
    is_clickable: bool = False
    is_checked: bool | None = None
    attributes: dict[str, str] = Field(default_factory=dict)


class FormFieldInfo(BaseModel):
    name: str
    field_type: str  # text, email, tel, password, file, select, checkbox, radio, textarea
    label: str | None = None
    placeholder: str | None = None
    required: bool = False
    current_value: str | None = None
    selector: str
    is_sensitive: bool = False


class FormInspectionResponse(BaseModel):
    form_id: str | None = None
    action_url: str | None = None
    method: str = "POST"
    fields: list[FormFieldInfo] = Field(default_factory=list)
    submit_button_selector: str | None = None
    submit_button_text: str | None = None


class DOMInspectionRequest(BaseModel):
    tab_id: str | None = None
    max_elements: int = Field(default=100, ge=10, le=1000)
    interactive_only: bool = True
    include_forms: bool = True


class DOMInspectionResponse(BaseModel):
    session_id: str
    tab_id: str
    url: str
    title: str
    elements: list[DOMElementNode] = Field(default_factory=list)
    forms: list[FormInspectionResponse] = Field(default_factory=list)
    total_elements_count: int = 0
    token_estimate: int = 0


class BrowserActionRequest(BaseModel):
    action_type: BrowserActionType
    target_locator: str | None = None
    tab_id: str | None = None
    parameters: dict[str, Any] = Field(default_factory=dict)
    timeout_ms: int = Field(default=15000, ge=500, le=60000)


class BrowserActionResponse(BaseModel):
    id: str
    session_id: str
    tab_id: str | None = None
    action_type: BrowserActionType
    status: BrowserActionStatus
    result: dict[str, Any] | None = None
    error_message: str | None = None
    screenshot_path: str | None = None
    duration_ms: float = 0.0


class BrowserBatchActionsRequest(BaseModel):
    tab_id: str | None = None
    actions: list[BrowserActionRequest]
    stop_on_failure: bool = True


class BrowserBatchActionsResponse(BaseModel):
    session_id: str
    total_actions: int
    succeeded_count: int
    failed_count: int
    results: list[BrowserActionResponse] = Field(default_factory=list)


class BrowserScreenshotRequest(BaseModel):
    tab_id: str | None = None
    full_page: bool = False
    element_locator: str | None = None
    quality: int = Field(default=80, ge=10, le=100)


class BrowserScreenshotResponse(BaseModel):
    session_id: str
    tab_id: str
    screenshot_path: str
    thumbnail_base64: str | None = None
    width: int
    height: int
    captured_at: datetime


class BrowserDownloadResponse(BaseModel):
    id: str
    session_id: str
    tab_id: str | None = None
    suggested_filename: str
    destination_path: str
    file_size_bytes: int
    sha256_checksum: str | None = None
    mime_type: str | None = None
    source_url: str
    status: BrowserDownloadStatus
    created_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None


class BrowserProfileCreateRequest(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: str = ""
    domain_scopes: list[str] = Field(default_factory=list)


class BrowserProfileResponse(BaseModel):
    id: str
    name: str
    description: str
    storage_path: str
    is_authenticated: bool
    domain_scopes: list[str]
    last_used_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class BrowserTaskCreateRequest(BaseModel):
    goal: str = Field(min_length=3)
    session_id: str | None = None
    workflow_id: str | None = None
    step_id: str | None = None
    max_steps: int = Field(default=15, ge=1, le=50)


class BrowserTaskResponse(BaseModel):
    id: str
    agent_id: str
    session_id: str | None = None
    workflow_id: str | None = None
    step_id: str | None = None
    goal: str
    status: BrowserTaskStatus
    current_step: int
    total_steps: int
    result: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: datetime
    started_at: datetime | None = None
    completed_at: datetime | None = None


class BrowserRuntimeStatus(BaseModel):
    playwright_available: bool
    installed_browsers: list[str]
    system_browsers_detected: list[str]
    active_sessions_count: int
    max_concurrent_sessions: int
    default_headless: bool
    downloads_dir: str
    screenshots_dir: str
