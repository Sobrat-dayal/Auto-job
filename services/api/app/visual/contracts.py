"""Strongly-typed data contracts and schemas for Visual Computer Control (Stage 18)."""

from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal
from uuid import uuid4
from pydantic import BaseModel, Field, PrivateAttr, model_validator


class CaptureProviderType(StrEnum):
    MSS = "mss"
    GDI = "gdi"
    WGC = "wgc"
    DXGI = "dxgi"
    MSS_DIRECT = "mss_direct"
    GDI_PRINT_WINDOW = "gdi_print_window"
    WINDOWS_GRAPHICS_CAPTURE = "windows_graphics_capture"
    DXGI_DESKTOP_DUPLICATION = "dxgi_desktop_duplication"


class CaptureTargetType(StrEnum):
    WINDOW = "window"
    DISPLAY = "display"
    REGION = "region"


class CaptureSessionState(StrEnum):
    CREATED = "created"
    WAITING_FOR_SELECTION = "waiting_for_selection"
    STARTING = "starting"
    ACTIVE = "active"
    CAPTURING = "active"
    PAUSED = "paused"
    STOPPING = "stopping"
    STOPPED = "stopped"
    FAILED = "failed"
    UNAVAILABLE = "unavailable"


class VisualActionType(StrEnum):
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    MOVE_POINTER = "move_pointer"
    SCROLL = "scroll"
    DRAG = "drag"
    PRESS_KEY = "press_key"
    ENTER_TEXT = "enter_text"
    HOVER = "hover"
    CLEAR_TEXT = "clear_text"


class VisualTaskStatus(StrEnum):
    PENDING = "pending"
    OBSERVING = "observing"
    GROUNDING = "grounding"
    ACTING = "acting"
    VERIFYING = "verifying"
    RECOVERING = "recovering"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"


class VerificationStatus(StrEnum):
    VERIFIED_SUCCESS = "verified_success"
    VERIFIED_FAILURE = "verified_failure"
    UNKNOWN_OUTCOME = "unknown_outcome"
    NEEDS_REVIEW = "needs_review"
    VERIFIED = "verified"
    FAILED = "failed"
    UNCERTAIN = "uncertain"
    SKIPPED = "skipped"


class ElementCategory(StrEnum):
    BUTTON = "button"
    INPUT = "input"
    CHECKBOX = "checkbox"
    COMBOBOX = "combobox"
    MENU = "menu"
    LINK = "link"
    TEXT = "text"
    TAB = "tab"
    SCROLLBAR = "scrollbar"
    DIALOG = "dialog"
    ICON = "icon"
    PANEL = "panel"
    UNKNOWN = "unknown"


# --- Geometry & Bounds ---

class Point2D(BaseModel):
    x: int
    y: int


class BoundingBox(BaseModel):
    left: int
    top: int
    width: int = Field(ge=0)
    height: int = Field(ge=0)

    @property
    def right(self) -> int:
        return self.left + self.width

    @property
    def bottom(self) -> int:
        return self.top + self.height

    @property
    def center(self) -> Point2D:
        return Point2D(x=self.left + self.width // 2, y=self.top + self.height // 2)

    def contains(self, point: Point2D) -> bool:
        return (
            self.left <= point.x <= self.right
            and self.top <= point.y <= self.bottom
        )


class NormalizedBox(BaseModel):
    """Normalized coordinates ranging from 0.0 to 1.0 relative to image frame."""
    x_min: float = 0.0
    y_min: float = 0.0
    x_max: float = 1.0
    y_max: float = 1.0

    model_config = {"populate_by_name": True, "extra": "allow"}

    @model_validator(mode="before")
    @classmethod
    def remap_aliases(cls, data: Any) -> Any:
        if isinstance(data, dict):
            d = dict(data)
            if "xmin" in d and "x_min" not in d:
                d["x_min"] = d["xmin"]
            if "ymin" in d and "y_min" not in d:
                d["y_min"] = d["ymin"]
            if "xmax" in d and "x_max" not in d:
                d["x_max"] = d["xmax"]
            if "ymax" in d and "y_max" not in d:
                d["y_max"] = d["ymax"]
            return d
        return data

    @property
    def xmin(self) -> float:
        return self.x_min

    @property
    def ymin(self) -> float:
        return self.y_min

    @property
    def xmax(self) -> float:
        return self.x_max

    @property
    def ymax(self) -> float:
        return self.y_max

    def to_pixel_box(self, width: int, height: int) -> BoundingBox:
        left = int(self.x_min * width)
        top = int(self.y_min * height)
        bw = max(1, int((self.x_max - self.x_min) * width))
        bh = max(1, int((self.y_max - self.y_min) * height))
        return BoundingBox(left=left, top=top, width=bw, height=bh)


class DisplayInfo(BaseModel):
    id: int = 1
    display_index: int = 0
    name: str = "Display 1"
    left: int = 0
    top: int = 0
    width: int = 1920
    height: int = 1080
    right: int = 1920
    bottom: int = 1080
    is_primary: bool = False
    dpi: int = 96
    scale_factor: float = 1.0
    orientation: str = "landscape"

    model_config = {"populate_by_name": True, "extra": "allow"}

    @model_validator(mode="before")
    @classmethod
    def remap_display_fields(cls, data: Any) -> Any:
        if isinstance(data, dict):
            d = dict(data)
            if "id" in d and "display_index" not in d:
                d["display_index"] = d["id"] - 1 if isinstance(d["id"], int) else 0
            elif "display_index" in d and "id" not in d:
                d["id"] = d["display_index"] + 1 if isinstance(d["display_index"], int) else 1
            if "right" not in d and "left" in d and "width" in d:
                d["right"] = d["left"] + d["width"]
            if "bottom" not in d and "top" in d and "height" in d:
                d["bottom"] = d["top"] + d["height"]
            return d
        return data


# --- Frame & Preprocessing ---

class FrameMetadata(BaseModel):
    frame_id: str = Field(default_factory=lambda: f"frm_{uuid4().hex[:12]}")
    session_id: str = "default_session"
    target_type: CaptureTargetType = CaptureTargetType.DISPLAY
    target_id: str = "display_0"
    timestamp: Any = Field(default_factory=lambda: datetime.now(UTC))
    provider: CaptureProviderType = CaptureProviderType.MSS
    width: int = 1920
    height: int = 1080
    scaled_width: int | None = None
    scaled_height: int | None = None
    scale_factor: float = 1.0
    crop_box: BoundingBox | None = None
    display_id: int | None = None
    display_index: int = 0
    target_hwnd: int | None = None
    window_ref: str | None = None
    dpi: int = 96
    content_hash: str | None = None
    is_fresh: bool = True

    model_config = {"populate_by_name": True, "extra": "allow"}

    def __init__(self, **data: Any) -> None:
        if "dpi_scale" in data and "scale_factor" not in data:
            data["scale_factor"] = data["dpi_scale"]
        w = data.get("width", 1920)
        h = data.get("height", 1080)
        if "scaled_width" not in data or data["scaled_width"] is None:
            data["scaled_width"] = w
        if "scaled_height" not in data or data["scaled_height"] is None:
            data["scaled_height"] = h
        super().__init__(**data)

    @property
    def dpi_scale(self) -> float:
        return self.scale_factor


class CapturedFrame(BaseModel):
    metadata: FrameMetadata
    base64_png: str | None = None
    _image: Any = PrivateAttr(default=None)

    def __init__(self, **data: Any) -> None:
        raw_img = data.pop("image", None)
        super().__init__(**data)
        if raw_img is not None:
            self._image = raw_img

    @property
    def frame_id(self) -> str:
        return self.metadata.frame_id

    @property
    def image(self) -> Any:
        if self._image is not None:
            return self._image
        if self.base64_png:
            try:
                import base64
                from io import BytesIO
                from PIL import Image
                raw_bytes = base64.b64decode(self.base64_png)
                self._image = Image.open(BytesIO(raw_bytes))
                return self._image
            except Exception:
                return None
        return None

    @image.setter
    def image(self, val: Any) -> None:
        self._image = val


# --- OCR & Visual Grounding ---

class OCRWord(BaseModel):
    text: str
    bounding_box: BoundingBox
    confidence: float = 1.0


class OCRLine(BaseModel):
    text: str
    words: list[OCRWord] = Field(default_factory=list)
    bounding_box: BoundingBox


class OCRResult(BaseModel):
    text: str
    lines: list[OCRLine] = Field(default_factory=list)
    language: str = "en"
    duration_ms: float = 0.0

    @property
    def full_text(self) -> str:
        return self.text


class VisualElementDetection(BaseModel):
    detection_id: str = Field(default_factory=lambda: f"det_{uuid4().hex[:8]}")
    frame_id: str
    category: ElementCategory = ElementCategory.UNKNOWN
    label: str | None = None
    bounding_box: BoundingBox
    normalized_box: NormalizedBox
    confidence: float = 1.0
    source: str = "vision_model"  # vision_model, ocr, hybrid, heuristic


class VisualGroundingResult(BaseModel):
    grounding_id: str = Field(default_factory=lambda: f"grd_{uuid4().hex[:8]}")
    frame_id: str
    query: str
    candidates: list[VisualElementDetection] = Field(default_factory=list)
    selected_target: VisualElementDetection | None = None
    target_point: Point2D | None = None  # Image-relative coordinates
    desktop_point: Point2D | None = None  # Desktop physical coordinates
    ambiguity_status: str = "unique"  # unique, ambiguous, none
    confidence: float = 1.0
    reasoning: str | None = None
    bounding_box: BoundingBox | None = None
    category: ElementCategory = ElementCategory.UNKNOWN

    @property
    def success(self) -> bool:
        return self.target_point is not None or self.selected_target is not None


# --- Actions & Tasks ---

class VisualActionRequest(BaseModel):
    action_type: VisualActionType
    session_id: str | None = None
    window_ref: str | None = None
    target_point: Point2D | None = None
    end_point: Point2D | None = None  # for drag
    text_value: str | None = None
    key: str | None = None
    modifiers: list[str] = Field(default_factory=list)
    scroll_delta: int = 120
    duration_ms: float = 100.0
    verify: bool = True
    expected_text: str | None = None


class VisualActionResult(BaseModel):
    action_id: str = Field(default_factory=lambda: f"act_{uuid4().hex[:10]}")
    action_type: VisualActionType
    status: str = "succeeded"  # succeeded, failed, blocked
    verification_status: VerificationStatus = VerificationStatus.UNKNOWN_OUTCOME
    duration_ms: float = 0.0
    target_point: Point2D | None = None
    desktop_point: Point2D | None = None
    before_frame_id: str | None = None
    after_frame_id: str | None = None
    diff_percentage: float | None = None
    error_message: str | None = None
    executed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class VisualTaskRequest(BaseModel):
    goal: str = ""
    instruction: str = ""
    session_id: str | None = None
    target_type: CaptureTargetType | None = None
    target_hwnd: int | None = None
    target_app: str | None = None
    target_window_ref: str | None = None
    display_index: int = 0
    provider: CaptureProviderType | None = None
    max_steps: int = Field(default=10, ge=1, le=50)
    timeout_seconds: float = Field(default=60.0, ge=5.0, le=600.0)
    privacy_mode: bool = True

    def __init__(self, **data: Any) -> None:
        if "instruction" in data and not data.get("goal"):
            data["goal"] = data["instruction"]
        elif "goal" in data and not data.get("instruction"):
            data["instruction"] = data["goal"]
        super().__init__(**data)


class VisualTaskResponse(BaseModel):
    task_id: str = Field(default_factory=lambda: f"vtsk_{uuid4().hex[:10]}")
    instruction: str = ""
    goal: str = ""
    status: VisualTaskStatus = VisualTaskStatus.PENDING
    steps_completed: int = 0
    total_steps: int = 1
    current_step: int = 0
    target_app: str | None = None
    actions: list[VisualActionResult] = Field(default_factory=list)
    result_summary: str | None = None
    result_data: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: Any = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    updated_at: Any = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    completed_at: datetime | None = None

    def __init__(self, **data: Any) -> None:
        if "instruction" in data and not data.get("goal"):
            data["goal"] = data["instruction"]
        elif "goal" in data and not data.get("instruction"):
            data["instruction"] = data["goal"]
        if "steps_completed" in data and "current_step" not in data:
            data["current_step"] = data["steps_completed"]
        super().__init__(**data)


class CaptureSessionCreateRequest(BaseModel):
    target_type: CaptureTargetType = CaptureTargetType.DISPLAY
    target_id: str = "display_0"  # window_ref or display_id
    provider: CaptureProviderType | None = None
    preferred_provider: CaptureProviderType | None = None
    display_index: int = 0
    target_hwnd: int | None = None
    frame_rate_limit: float = Field(default=5.0, ge=0.5, le=30.0)
    privacy_mode: bool = True

    def __init__(self, **data: Any) -> None:
        if "provider" in data and "preferred_provider" not in data:
            data["preferred_provider"] = data["provider"]
        elif "preferred_provider" in data and "provider" not in data:
            data["provider"] = data["preferred_provider"]
        if "display_index" in data and "target_id" not in data:
            data["target_id"] = f"display_{data['display_index']}"
        super().__init__(**data)


class CaptureSessionResponse(BaseModel):
    session_id: str = Field(default_factory=lambda: f"vsess_{uuid4().hex[:10]}")
    state: CaptureSessionState = CaptureSessionState.CAPTURING
    target_type: CaptureTargetType = CaptureTargetType.DISPLAY
    target_id: str = "display_0"
    provider: CaptureProviderType = CaptureProviderType.MSS
    display_index: int = 0
    target_hwnd: int | None = None
    frame_rate_limit: float = 5.0
    frames_captured: int = 0
    frame_count: int = 0
    fps: float = 0.0
    current_frame: CapturedFrame | None = None
    created_at: Any = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: Any = Field(default_factory=lambda: datetime.now(UTC))
    last_frame_at: datetime | None = None


class VisualDiagnosticsInfo(BaseModel):
    active_provider: CaptureProviderType = CaptureProviderType.MSS
    available_providers: list[Any] = Field(default_factory=lambda: [CaptureProviderType.MSS, CaptureProviderType.GDI, CaptureProviderType.WGC])
    active_sessions_count: int = 0
    monitors_count: int = 1
    primary_display_resolution: str = "1920x1080"
    dpi_scaling_factor: float = 1.0
    offline_windows_ocr_available: bool = True
    vlm_grounding_available: bool = True
    gpu_acceleration: bool = True
    last_capture_latency_ms: float = 16.0
    last_ocr_latency_ms: float = 45.0
    active_emergency_stop: bool = False
    active_sessions: int = 0
    total_frames_captured: int = 0
    displays: list[DisplayInfo] = Field(default_factory=list)
    ocr_available: bool = True
    ocr_engine: str = "windows_media_ocr"
    vision_model: str = "vlm_local"
    emergency_stop_active: bool = False
    gpu_utilization: float | None = None
    diagnostic_timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))

