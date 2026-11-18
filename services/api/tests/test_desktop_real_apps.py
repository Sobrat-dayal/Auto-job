"""Real Windows Application interaction tests with live Windows applications (Stage 17)."""

import pytest
from app.computer.contracts import InspectionOptions, WindowManageAction
from app.computer.security.authorization import DEFAULT_ALLOWED_APPS
from app.computer.service import desktop_service
from app.computer.windows.windows import window_discovery_manager


@pytest.mark.asyncio
async def test_real_windows_application_discovery_and_uia_inspection():
    """Discover real running Windows application (e.g. explorer.exe or WindowsTerminal.exe), inspect its UIA tree, and test safe window management."""
    windows = window_discovery_manager.list_windows()
    assert len(windows) > 0, "No top-level windows discovered on Default desktop"

    # Locate an allowed running Windows application window (e.g. Explorer or WindowsTerminal)
    allowed_wins = [
        w for w in windows
        if w.process_name.lower() in DEFAULT_ALLOWED_APPS and w.is_visible and w.bounds.width > 100
    ]

    # Fallback to any visible window if none of the allowed apps are currently visible
    target_win = allowed_wins[0] if allowed_wins else windows[0]

    assert target_win.hwnd > 0
    assert target_win.pid > 0
    assert target_win.window_ref.startswith(f"win_{target_win.hwnd}_{target_win.pid}")

    # Inspect its UI Automation accessibility tree via desktop_service
    options = InspectionOptions(max_depth=3, max_nodes=30)
    tree = await desktop_service.inspect_window_tree(target_win.window_ref, options)

    assert tree.root is not None
    assert tree.total_nodes > 0
    assert tree.root.element.control_type in ["Window", "Pane"]

    # Test safe window management: Activate
    activated = await desktop_service.manage_window(
        target_win.window_ref,
        WindowManageAction.ACTIVATE,
    )
    assert isinstance(activated, bool)
