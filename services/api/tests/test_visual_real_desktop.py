"""Real live desktop integration tests for Visual Automation (Stage 18).

Executes against the real Windows 11 desktop, capturing actual display frames,
extracting text via native offline WinRT OCR, and grounding visual UI targets.
"""

import pytest
from app.visual.capture.monitors import MonitorDiscoveryManager
from app.visual.capture.providers import CaptureProviderRegistry
from app.visual.contracts import CaptureProviderType, CaptureSessionCreateRequest, CaptureTargetType
from app.visual.grounding.ocr import WindowsMediaOCREngine
from app.visual.service import VisualComputerService


@pytest.mark.asyncio
async def test_live_desktop_screen_capture():
    """Captures real screen from physical primary monitor and validates resolution and format."""
    provider = CaptureProviderRegistry.get_provider(CaptureProviderType.MSS)
    img = provider.capture_display(display_id=0)

    assert img is not None
    assert img.size[0] >= 800
    assert img.size[1] >= 600
    assert img.mode == "RGB"


@pytest.mark.asyncio
async def test_live_desktop_offline_winrt_ocr():
    """Runs genuine offline WinRT OCR against the live desktop screenshot."""
    ocr = WindowsMediaOCREngine()
    if not ocr.is_available:
        pytest.skip("WinRT Windows Media OCR not available on this machine")

    provider = CaptureProviderRegistry.get_provider(CaptureProviderType.MSS)
    img = provider.capture_display(display_id=0)

    ocr_result = await ocr.extract_text_from_image(img)
    assert ocr_result.duration_ms >= 0.0
    # Any desktop with Windows running will have at least some text (taskbar, clock, icons, or terminal)
    assert isinstance(ocr_result.lines, list)
    if ocr_result.lines:
        first_line = ocr_result.lines[0]
        assert first_line.text is not None
        assert first_line.bounding_box.width > 0
        assert first_line.bounding_box.height > 0


@pytest.mark.asyncio
async def test_live_visual_service_grounding():
    """Tests VisualComputerService grounding against the active desktop."""
    service = VisualComputerService.get_instance()
    sess = await service.create_session(
        CaptureSessionCreateRequest(
            target_type=CaptureTargetType.DISPLAY,
            display_index=0,
            provider=CaptureProviderType.MSS,
        )
    )

    try:
        frame = await service.capture_frame(sess.session_id)
        assert frame.image.width > 0

        elements = await service.detect_elements(sess.session_id)
        assert isinstance(elements, list)
    finally:
        await service.close_session(sess.session_id)
