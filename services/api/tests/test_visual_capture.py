"""Tests for Windows screen capture providers, preprocessing, and session management (Stage 18)."""

import pytest
from PIL import Image
from app.visual.contracts import (
    BoundingBox,
    CaptureProviderType,
    CaptureSessionCreateRequest,
    CaptureTargetType,
)
from app.visual.capture.monitors import MonitorDiscoveryManager
from app.visual.capture.preprocessing import FramePreprocessor
from app.visual.capture.providers import CaptureProviderRegistry
from app.visual.capture.sessions import CaptureSessionManager


def test_monitor_discovery():
    """Test physical monitor discovery and bounds calculation."""
    monitors = MonitorDiscoveryManager.discover_monitors()
    assert len(monitors) >= 1
    primary = monitors[0]
    assert primary.width > 0
    assert primary.height > 0
    assert primary.scale_factor >= 1.0
    assert primary.dpi > 0

    virtual_rect = MonitorDiscoveryManager.get_virtual_desktop_rect()
    assert virtual_rect["width"] >= primary.width
    assert virtual_rect["height"] >= primary.height


def test_frame_preprocessing():
    """Test image resizing, cropping, content hashing, and redaction."""
    img = Image.new("RGB", (1920, 1080), color=(100, 150, 200))
    resized = FramePreprocessor.resize_preserving_aspect(img, max_dim=800)
    assert max(resized.size) == 800
    assert resized.size[0] == 800
    assert resized.size[1] == 450

    cropped = FramePreprocessor.crop_region(img, BoundingBox(left=100, top=100, width=200, height=150))
    assert cropped.size == (200, 150)

    # Redaction
    redacted = FramePreprocessor.redact_regions(img, [BoundingBox(left=50, top=50, width=50, height=50)])
    assert redacted.size == img.size
    # Redacted area should be black
    assert redacted.getpixel((60, 60)) == (0, 0, 0)

    # Hashing
    h1 = FramePreprocessor.compute_content_hash(img)
    h2 = FramePreprocessor.compute_content_hash(redacted)
    assert len(h1) == 64
    assert h1 != h2

    # Frame difference
    diff = FramePreprocessor.compute_frame_difference(img, redacted)
    assert diff > 0.0


@pytest.mark.asyncio
async def test_capture_session_lifecycle():
    """Test creating, capturing from, and closing a capture session."""
    mgr = CaptureSessionManager()
    req = CaptureSessionCreateRequest(
        target_type=CaptureTargetType.DISPLAY,
        display_index=0,
        provider=CaptureProviderType.MSS,
    )
    sess = await mgr.create_session(req)
    assert sess.session_id.startswith("vsess_")
    assert sess.display_index == 0

    # Capture a frame
    frame = await mgr.capture_frame(sess.session_id)
    assert frame.metadata.width > 0
    assert frame.metadata.height > 0
    assert frame.image.size == (frame.metadata.width, frame.metadata.height)

    # Close session
    closed = await mgr.close_session(sess.session_id)
    assert closed is True
    assert mgr.get_session(sess.session_id) is None
