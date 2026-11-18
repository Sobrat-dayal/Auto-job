"""Tests for Windows Media OCR and visual UI element grounding (Stage 18)."""

import pytest
from PIL import Image, ImageDraw, ImageFont
from app.visual.contracts import (
    BoundingBox,
    ElementCategory,
    FrameMetadata,
    VisualElementDetection,
)
from app.visual.grounding.ocr import WindowsMediaOCREngine
from app.visual.grounding.validation import TargetValidator
from app.visual.grounding.vision import VisualGroundingService


@pytest.fixture
def synthetic_text_image():
    """Generates an image with clearly rendered text for OCR testing."""
    img = Image.new("RGB", (600, 300), color=(255, 255, 255))
    draw = ImageDraw.Draw(img)
    # Draw dark text on white background
    draw.text((50, 50), "AUTONOM RECRUITMENT", fill=(0, 0, 0))
    draw.text((50, 120), "Apply Now", fill=(0, 0, 0))
    draw.text((250, 120), "Cancel", fill=(0, 0, 0))
    draw.text((50, 200), "Search Candidates", fill=(0, 0, 0))
    return img


@pytest.mark.asyncio
async def test_ocr_extract_and_match(synthetic_text_image):
    """Test offline OCR extraction on synthetic image."""
    engine = WindowsMediaOCREngine()
    if not engine.is_available:
        pytest.skip("WinRT Windows Media OCR not available in test environment")

    res = await engine.extract_text_from_image(synthetic_text_image)
    assert len(res.lines) >= 1
    full_lower = res.full_text.lower()
    assert "apply" in full_lower or "cancel" in full_lower or "autonom" in full_lower

    # Test text target matching
    matches = engine.find_text_targets(res, "Cancel")
    assert len(matches) >= 1
    match_text, box, score = matches[0]
    assert "cancel" in match_text.lower()
    assert box.width > 0
    assert box.height > 0
    assert score >= 0.8


@pytest.mark.asyncio
async def test_visual_grounding_query(synthetic_text_image):
    """Test visual grounding service locating controls."""
    service = VisualGroundingService()
    meta = FrameMetadata(
        frame_id="f_test",
        session_id="s_test",
        timestamp="2026-11-18T00:00:00Z",
        target_type="display",
        width=synthetic_text_image.width,
        height=synthetic_text_image.height,
        dpi_scale=1.0,
        content_hash="test",
    )

    if not service._ocr.is_available:
        pytest.skip("WinRT OCR not available")

    # Ground query "Apply Now"
    res = await service.ground_query(synthetic_text_image, meta, "Apply Now")
    assert res.success is True
    assert res.target_point is not None
    assert res.target_point.x > 0
    assert res.target_point.y > 0
    assert res.confidence >= 0.7


def test_target_validator_disambiguation():
    """Test target validator handling ambiguous candidate elements."""
    meta = FrameMetadata(
        frame_id="f_ambig",
        session_id="s_ambig",
        timestamp="2026-11-18T00:00:00Z",
        target_type="display",
        width=1920,
        height=1080,
        dpi_scale=1.0,
        content_hash="ambig",
    )

    c1 = VisualElementDetection(
        frame_id="f_ambig",
        category=ElementCategory.BUTTON,
        label="Save Document",
        bounding_box=BoundingBox(left=100, top=100, width=120, height=40),
        normalized_box={"ymin": 0.1, "xmin": 0.1, "ymax": 0.2, "xmax": 0.2},
        confidence=0.95,
        source="ocr",
    )
    c2 = VisualElementDetection(
        frame_id="f_ambig",
        category=ElementCategory.TEXT,
        label="Save As...",
        bounding_box=BoundingBox(left=100, top=200, width=100, height=30),
        normalized_box={"ymin": 0.2, "xmin": 0.1, "ymax": 0.3, "xmax": 0.2},
        confidence=0.85,
        source="ocr",
    )

    validator = TargetValidator()
    # Query "Save Document" should unambiguously select c1
    result = validator.resolve_target("Save Document", [c1, c2], meta)
    assert result.success is True
    assert result.target_point is not None
    # Center of c1 is (100 + 60, 100 + 20) = (160, 120)
    assert result.target_point.x == 160
    assert result.target_point.y == 120
