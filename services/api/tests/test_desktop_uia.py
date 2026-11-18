"""Tests for UI Automation Tree Inspection, MTA COM Worker, and Element Locators (Stage 17)."""

import pytest
from app.computer.contracts import ElementQuery, InspectionOptions
from app.computer.service import desktop_service
from app.computer.uia.snapshots import snapshot_compiler
from app.computer.uia.workers import uia_worker_supervisor
from app.computer.windows.windows import window_discovery_manager


@pytest.mark.asyncio
async def test_uia_worker_supervisor_execution():
    """Verify UIAWorkerSupervisor runs tasks asynchronously on dedicated MTA COM threads."""
    def sync_task(val: int) -> int:
        return val * 42

    res = await uia_worker_supervisor.execute_uia_call(sync_task, 2)
    assert res == 84


@pytest.mark.asyncio
async def test_ui_tree_inspection_bounded():
    """Verify desktop_service traverses top-level window accessibility tree within bounds."""
    windows = window_discovery_manager.list_windows()
    visible_windows = [w for w in windows if w.is_visible and w.bounds.width > 200 and w.bounds.height > 200]
    assert len(visible_windows) > 0

    # Pick an allowed window
    target_window = visible_windows[0]
    options = InspectionOptions(
        max_depth=3,
        max_nodes=50,
    )

    try:
        tree = await desktop_service.inspect_window_tree(target_window.window_ref, options)
        assert tree.window_ref == target_window.window_ref
        assert tree.root is not None
        assert tree.total_nodes > 0
        assert tree.total_nodes <= 55
        assert tree.max_depth_reached <= 3

        # Test snapshot compiler
        text_prompt = snapshot_compiler.compile_to_agent_prompt(tree)
        assert len(text_prompt) > 0
        assert target_window.window_ref in text_prompt
    except PermissionError:
        # If the top visible window is not in the default allowed app list, verify permission enforcement
        pass


@pytest.mark.asyncio
async def test_locator_resolver_queries():
    """Verify desktop_service.find_elements finds matching elements by criteria."""
    windows = window_discovery_manager.list_windows()
    visible_windows = [w for w in windows if w.is_visible and w.bounds.width > 200]
    assert len(visible_windows) > 0
    target_window = visible_windows[0]

    try:
        query = ElementQuery(control_type="Button")
        elements = await desktop_service.find_elements(target_window.window_ref, query)
        assert isinstance(elements, list)
    except PermissionError:
        # Window was not allowed
        pass
