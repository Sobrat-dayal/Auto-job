"""Tests for Windows Discovery, Window Ref Validation, and Lifetime Verification (Stage 17)."""

import pytest
from app.computer.windows.windows import window_discovery_manager


def test_window_discovery_enumeration():
    """Verify window discovery enumerates active top-level desktop windows."""
    windows = window_discovery_manager.list_windows()

    assert isinstance(windows, list)
    assert len(windows) > 0

    # Every window should have valid metadata and window_ref
    for win in windows[:10]:
        assert win.hwnd > 0
        assert win.pid > 0
        assert win.window_ref.startswith(f"win_{win.hwnd}_{win.pid}")
        assert win.process_name is not None
        assert win.bounds is not None
        assert win.bounds.width >= 0
        assert win.bounds.height >= 0


def test_window_ref_validation_and_resolution():
    """Verify valid window_ref resolves to existing window and invalid window_ref returns None."""
    windows = window_discovery_manager.list_windows()
    assert len(windows) > 0

    target = windows[0]
    # Valid resolution
    validated = window_discovery_manager.validate_window_ref(target.window_ref)
    assert validated is not None
    assert validated.hwnd == target.hwnd

    # Invalid window_ref format returns None
    assert window_discovery_manager.validate_window_ref("invalid_ref_format") is None

    # Non-existent HWND / recycled PID mismatch returns None
    assert window_discovery_manager.validate_window_ref("win_99999999_99999") is None


def test_window_filtering():
    """Verify window discovery with include_invisible filters properly."""
    visible = window_discovery_manager.list_windows(include_invisible=False)
    all_wins = window_discovery_manager.list_windows(include_invisible=True)

    assert len(all_wins) >= len(visible)
    for win in visible:
        assert win.is_visible is True
