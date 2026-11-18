"""Capture session lifecycle, frame acquisition, and target management (Stage 18)."""

import asyncio
from datetime import UTC, datetime
import logging
from typing import Any
from uuid import uuid4
from PIL import Image

from app.computer.windows.windows import window_discovery_manager
from app.visual.capture.frames import FrameBuffer
from app.visual.capture.monitors import monitor_discovery_manager
from app.visual.capture.preprocessing import frame_preprocessor
from app.visual.capture.providers import capture_provider_registry
from app.visual.contracts import (
    BoundingBox,
    CaptureProviderType,
    CaptureSessionCreateRequest,
    CaptureSessionResponse,
    CaptureSessionState,
    CaptureTargetType,
    CapturedFrame,
    FrameMetadata,
)

logger = logging.getLogger("autonom.visual.capture.sessions")


class CaptureSessionInstance:
    """Active runtime instance of a visual screen capture session."""

    def __init__(
        self,
        session_id: str,
        target_type: CaptureTargetType,
        target_id: str,
        provider_type: CaptureProviderType,
        frame_rate_limit: float = 5.0,
        privacy_mode: bool = True,
    ) -> None:
        self.session_id = session_id
        self.target_type = target_type
        self.target_id = target_id
        self.provider_type = provider_type
        self.frame_rate_limit = frame_rate_limit
        self.privacy_mode = privacy_mode
        self.state = CaptureSessionState.STARTING
        self.created_at = datetime.now(UTC)
        self.last_frame_at: datetime | None = None
        self.frame_count = 0
        self.buffer = FrameBuffer(max_capacity=10, max_age_seconds=5.0)
        self._provider = capture_provider_registry.get_provider(provider_type)

    def capture_single_frame(self) -> tuple[CapturedFrame, Image.Image]:
        """Captures a real physical frame from the designated target."""
        raw_image: Image.Image
        hwnd: int | None = None
        window_ref: str | None = None
        display_id: int | None = None
        box: BoundingBox | None = None

        if self.target_type == CaptureTargetType.WINDOW:
            # Resolve target_id as window_ref or HWND
            win = window_discovery_manager.validate_window_ref(self.target_id)
            if not win:
                # Attempt to find by HWND
                try:
                    target_hwnd = int(self.target_id)
                    all_wins = window_discovery_manager.list_windows(include_invisible=True)
                    match = [w for w in all_wins if w.hwnd == target_hwnd]
                    win = match[0] if match else None
                except ValueError:
                    win = None

            if not win:
                self.state = CaptureSessionState.FAILED
                raise ValueError(f"Target window closed or invalid reference: {self.target_id}")

            hwnd = win.hwnd
            window_ref = win.window_ref
            box = win.bounds
            raw_image = self._provider.capture_window(hwnd)

        elif self.target_type == CaptureTargetType.DISPLAY:
            try:
                display_id = int(self.target_id)
            except ValueError:
                display_id = 1
            raw_image = self._provider.capture_display(display_id)

        else:  # REGION
            raw_image = self._provider.capture_display(1)

        # Scale down if larger than model limits
        scaled_img, scale_factor = frame_preprocessor.scale_image(raw_image, max_dimension=1600)
        base64_str = frame_preprocessor.to_base64_png(scaled_img)
        content_hash = frame_preprocessor.compute_image_hash(scaled_img)

        now = datetime.now(UTC)
        self.last_frame_at = now
        self.frame_count += 1
        self.state = CaptureSessionState.ACTIVE

        metadata = FrameMetadata(
            session_id=self.session_id,
            target_type=self.target_type,
            target_id=self.target_id,
            timestamp=now,
            provider=self.provider_type,
            width=raw_image.size[0],
            height=raw_image.size[1],
            scaled_width=scaled_img.size[0],
            scaled_height=scaled_img.size[1],
            scale_factor=scale_factor,
            crop_box=box,
            display_id=display_id,
            window_ref=window_ref,
            content_hash=content_hash,
            is_fresh=True,
        )

        captured = CapturedFrame(metadata=metadata, base64_png=base64_str, image=raw_image)
        self.buffer.push_frame(captured, raw_image)
        return captured, raw_image

    def to_response(self) -> CaptureSessionResponse:
        latest = self.buffer.get_latest()
        current_frame = latest[0] if latest else None
        elapsed = (datetime.now(UTC) - self.created_at).total_seconds()
        fps = round(self.frame_count / max(1.0, elapsed), 2)
        display_idx = 0
        if self.target_type == CaptureTargetType.DISPLAY:
            try:
                display_idx = int(self.target_id.split("_")[-1])
            except Exception:
                display_idx = 0

        return CaptureSessionResponse(
            session_id=self.session_id,
            state=self.state,
            target_type=self.target_type,
            target_id=self.target_id,
            provider=self.provider_type,
            display_index=display_idx,
            frame_count=self.frame_count,
            fps=fps,
            current_frame=current_frame,
            created_at=self.created_at,
            last_frame_at=self.last_frame_at,
        )


class CaptureSessionManager:
    """Manages active visual capture sessions across displays and windows."""

    def __init__(self) -> None:
        self._sessions: dict[str, CaptureSessionInstance] = {}

    async def create_session(self, req: CaptureSessionCreateRequest) -> CaptureSessionResponse:
        """Initializes a new capture session and captures the first frame."""
        provider_type = req.preferred_provider or req.provider or CaptureProviderType.MSS
        # For window capture, GDI is preferred for direct window isolation
        if req.target_type == CaptureTargetType.WINDOW and not req.preferred_provider:
            provider_type = CaptureProviderType.GDI

        session_id = f"vsess_{uuid4().hex[:10]}"
        instance = CaptureSessionInstance(
            session_id=session_id,
            target_type=req.target_type,
            target_id=req.target_id,
            provider_type=provider_type,
            frame_rate_limit=req.frame_rate_limit,
            privacy_mode=req.privacy_mode,
        )

        # Capture first frame to establish active state
        instance.capture_single_frame()
        self._sessions[session_id] = instance
        return instance.to_response()

    def get_session(self, session_id: str) -> CaptureSessionResponse | None:
        """Retrieves session telemetry by ID."""
        instance = self._sessions.get(session_id)
        return instance.to_response() if instance else None

    def get_session_instance(self, session_id: str) -> CaptureSessionInstance | None:
        return self._sessions.get(session_id)

    def list_sessions(self) -> list[CaptureSessionResponse]:
        """Lists all active and recent capture sessions."""
        return [inst.to_response() for inst in self._sessions.values()]

    async def capture_frame(self, session_id: str) -> CapturedFrame:
        """Explicitly requests a fresh frame from the capture session."""
        instance = self._sessions.get(session_id)
        if not instance:
            raise KeyError(f"Capture session not found: {session_id}")
        captured, _ = instance.capture_single_frame()
        return captured

    def stop_session(self, session_id: str) -> bool:
        """Stops an active capture session and frees its frame buffers."""
        instance = self._sessions.pop(session_id, None)
        if not instance:
            return False
        instance.state = CaptureSessionState.STOPPED
        instance.buffer.clear()
        return True

    async def close_session(self, session_id: str) -> bool:
        """Async alias for stop_session."""
        return self.stop_session(session_id)


capture_session_manager = CaptureSessionManager()

