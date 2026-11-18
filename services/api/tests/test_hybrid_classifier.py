"""Unit tests for Target Surface Classification and Identity Validation."""

import pytest
from app.hybrid.contracts import InteractionTarget, SurfaceType, TargetType
from app.hybrid.errors import StaleTargetError
from app.hybrid.targets.classifier import SurfaceClassifier
from app.hybrid.targets.identity import TargetIdentityValidator


def test_surface_classifier_browser_dom() -> None:
    """Verifies that DOM selectors, browser sessions, and browser process names classify as BROWSER_DOM."""
    t1 = InteractionTarget(target_type=TargetType.BROWSER_ELEMENT, dom_selector="input[name='q']")
    assert SurfaceClassifier.classify(t1) == SurfaceType.BROWSER_DOM

    t2 = InteractionTarget(target_type=TargetType.BROWSER_PAGE, session_id="bsess_123")
    assert SurfaceClassifier.classify(t2) == SurfaceType.BROWSER_DOM

    t3 = InteractionTarget(target_type=TargetType.NATIVE_WINDOW, process_name="chrome.exe")
    assert SurfaceClassifier.classify(t3) == SurfaceType.BROWSER_DOM


def test_surface_classifier_native_uia() -> None:
    """Verifies that UIA elements, automation IDs, and native windows classify as NATIVE_UIA."""
    t1 = InteractionTarget(target_type=TargetType.UIA_ELEMENT, uia_runtime_id="btn_ok_42")
    assert SurfaceClassifier.classify(t1) == SurfaceType.NATIVE_UIA

    t2 = InteractionTarget(target_type=TargetType.NATIVE_WINDOW, window_ref="win_100_200")
    assert SurfaceClassifier.classify(t2) == SurfaceType.NATIVE_UIA


def test_surface_classifier_custom_rendered() -> None:
    """Verifies that coordinates and visual capture targets classify as CUSTOM_RENDERED."""
    t1 = InteractionTarget(target_type=TargetType.VISUAL_CAPTURE_TARGET)
    assert SurfaceClassifier.classify(t1) == SurfaceType.CUSTOM_RENDERED

    t2 = InteractionTarget(
        target_type=TargetType.NATIVE_WINDOW,
        control_type="pane",
        coordinates={"x": 400, "y": 300},
    )
    assert SurfaceClassifier.classify(t2) == SurfaceType.CUSTOM_RENDERED


def test_target_identity_validator_stale_dom_selector() -> None:
    """Verifies that empty DOM selector triggers StaleTargetError."""
    target = InteractionTarget(
        target_type=TargetType.BROWSER_ELEMENT,
        surface_type=SurfaceType.BROWSER_DOM,
        dom_selector="",
    )
    with pytest.raises(StaleTargetError) as exc_info:
        TargetIdentityValidator.validate_target(target)
    assert "DOM selector is empty" in str(exc_info.value)


def test_target_identity_validator_negative_coordinates() -> None:
    """Verifies that negative coordinate targets trigger StaleTargetError."""
    target = InteractionTarget(
        target_type=TargetType.VISUAL_CAPTURE_TARGET,
        surface_type=SurfaceType.CUSTOM_RENDERED,
        coordinates={"x": -10, "y": 200},
    )
    with pytest.raises(StaleTargetError) as exc_info:
        TargetIdentityValidator.validate_target(target)
    assert "Negative coordinates" in str(exc_info.value)


def test_target_identity_validator_valid_target() -> None:
    """Verifies that valid targets pass validation cleanly."""
    target = InteractionTarget(
        target_type=TargetType.BROWSER_ELEMENT,
        surface_type=SurfaceType.BROWSER_DOM,
        dom_selector="button.primary",
    )
    assert TargetIdentityValidator.validate_target(target) is True
