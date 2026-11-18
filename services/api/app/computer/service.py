"""Central Desktop Automation Service for Windows structural control (Stage 17)."""

import asyncio
from datetime import UTC, datetime
import logging
import os
import subprocess
import time
from uuid import uuid4

from app.computer.actions.executor import action_executor
from app.computer.contracts import (
    DesktopActionRequest,
    DesktopActionResult,
    DesktopApplicationInfo,
    DesktopDiagnosticsInfo,
    DesktopSessionInfo,
    DesktopTaskRequest,
    DesktopTaskResponse,
    ElementQuery,
    InspectionOptions,
    UIElementInfo,
    UITreeSnapshot,
    WindowInfo,
    WindowManageAction,
)
from app.computer.security.authorization import desktop_auth_policy
from app.computer.security.guard import desktop_security_guard
from app.computer.security.privacy import privacy_filter
from app.computer.uia.locators import locator_resolver
from app.computer.uia.trees import tree_inspector
from app.computer.uia.workers import uia_worker_supervisor
from app.computer.windows.management import window_state_manager
from app.computer.windows.processes import process_discovery_manager
from app.computer.windows.sessions import session_manager
from app.computer.windows.windows import window_discovery_manager
from app.security.authorization.emergency import get_emergency_stop_controller

logger = logging.getLogger("autonom.computer.service")


class DesktopAutomationService:
    """Coordinates Windows desktop application discovery, UI Automation tree inspection, and safe action execution."""

    def __init__(self) -> None:
        self._action_history: list[DesktopActionResult] = []
        self._tasks: dict[str, DesktopTaskResponse] = []
        self._tasks_dict: dict[str, DesktopTaskResponse] = {}

    def get_session_info(self) -> DesktopSessionInfo:
        """Returns interactive desktop session telemetry."""
        return session_manager.get_session_info()

    def list_applications(self) -> list[DesktopApplicationInfo]:
        """Discovers running desktop applications."""
        desktop_security_guard.assert_automation_allowed()
        return process_discovery_manager.list_running_applications()

    def list_windows(self, include_invisible: bool = False) -> list[WindowInfo]:
        """Enumerates active top-level windows on the interactive desktop."""
        desktop_security_guard.assert_automation_allowed()
        return window_discovery_manager.list_windows(include_invisible=include_invisible)

    def get_window(self, window_ref: str) -> WindowInfo | None:
        """Retrieves and validates a specific window reference."""
        desktop_security_guard.assert_automation_allowed()
        return window_discovery_manager.validate_window_ref(window_ref)

    async def inspect_window_tree(
        self,
        window_ref: str,
        options: InspectionOptions | None = None,
    ) -> UITreeSnapshot:
        """Inspects and returns a bounded accessibility tree for a validated window."""
        desktop_security_guard.assert_automation_allowed()

        win = window_discovery_manager.validate_window_ref(window_ref)
        if not win:
            raise ValueError(f"Window reference invalid or window has closed: {window_ref}")

        # Check authorization
        allowed, reason = desktop_auth_policy.validate_process_for_automation(win.pid, win.process_name)
        if not allowed:
            raise PermissionError(f"Access denied: {reason}")

        snapshot: UITreeSnapshot = await uia_worker_supervisor.execute_uia_call(
            tree_inspector.inspect_window_tree,
            win.hwnd,
            window_ref,
            win.title,
            options,
            timeout_seconds=float((options.timeout_ms if options else 10000) / 1000.0) + 2.0,
        )

        # Apply privacy sanitization
        sanitized_root = privacy_filter.sanitize_tree_node(snapshot.root)
        snapshot.root = sanitized_root
        return snapshot

    async def find_elements(
        self,
        window_ref: str,
        query: ElementQuery,
    ) -> list[UIElementInfo]:
        """Finds matching accessible elements in target window by locator."""
        desktop_security_guard.assert_automation_allowed()

        win = window_discovery_manager.validate_window_ref(window_ref)
        if not win:
            raise ValueError(f"Window reference invalid or window has closed: {window_ref}")

        def _do_find():
            results = locator_resolver.find_elements(win.hwnd, window_ref, query)
            return [info for _, info in results]

        return await uia_worker_supervisor.execute_uia_call(_do_find, timeout_seconds=10.0)

    async def execute_action(
        self,
        request: DesktopActionRequest,
    ) -> DesktopActionResult:
        """Executes a typed structural desktop action with safety boundaries and verification."""
        desktop_security_guard.assert_automation_allowed()

        win = window_discovery_manager.validate_window_ref(request.window_ref)
        if not win:
            raise ValueError(f"Window reference invalid or window has closed: {request.window_ref}")

        allowed, reason = desktop_auth_policy.validate_process_for_automation(win.pid, win.process_name)
        if not allowed:
            raise PermissionError(f"Action denied: {reason}")

        result: DesktopActionResult = await uia_worker_supervisor.execute_uia_call(
            action_executor.execute_action,
            request,
            timeout_seconds=float(request.timeout_ms / 1000.0) + 2.0,
        )

        self._action_history.append(result)
        return result

    async def manage_window(
        self,
        window_ref: str,
        action: WindowManageAction,
    ) -> bool:
        """Executes window state management (activate, minimize, maximize, restore, close)."""
        desktop_security_guard.assert_automation_allowed()

        win = window_discovery_manager.validate_window_ref(window_ref)
        if not win:
            raise ValueError(f"Window reference invalid or window has closed: {window_ref}")

        return await uia_worker_supervisor.execute_uia_call(
            window_state_manager.execute_window_action,
            window_ref,
            action,
            timeout_seconds=5.0,
        )

    def launch_application(
        self,
        executable_name: str,
        arguments: list[str] | None = None,
        working_dir: str | None = None,
    ) -> WindowInfo | None:
        """Safely launches an approved desktop application and discovers its main window."""
        desktop_security_guard.assert_automation_allowed()

        if not desktop_auth_policy.is_application_allowed(executable_name):
            raise PermissionError(f"Application '{executable_name}' is not in the approved desktop automation allowlist")

        args = [executable_name] + (arguments or [])
        try:
            proc = subprocess.Popen(
                args,
                cwd=working_dir or os.getcwd(),
                shell=False,
            )
        except Exception as e:
            logger.error(f"Failed to launch application {executable_name}: {e}")
            raise RuntimeError(f"Failed to launch application {executable_name}: {e}")

        # Wait up to 5 seconds for top-level window to appear
        for _ in range(25):
            time.sleep(0.2)
            windows = window_discovery_manager.list_windows()
            for w in windows:
                if w.pid == proc.pid:
                    return w

        # Return whatever window matched the process name if pid check missed child window
        for w in window_discovery_manager.list_windows():
            if w.process_name.lower() == executable_name.lower():
                return w

        return None

    def get_action_history(self, limit: int = 50) -> list[DesktopActionResult]:
        """Returns recent action execution history."""
        return list(reversed(self._action_history[-limit:]))

    def get_action(self, action_id: str) -> DesktopActionResult | None:
        """Retrieves action record by ID."""
        for a in self._action_history:
            if a.action_id == action_id:
                return a
        return None

    def submit_task(self, request: DesktopTaskRequest) -> DesktopTaskResponse:
        """Submits a desktop automation task."""
        desktop_security_guard.assert_automation_allowed()

        task_id = f"dtask_{uuid4().hex[:12]}"
        task = DesktopTaskResponse(
            task_id=task_id,
            goal=request.goal,
            target_app=request.target_app,
            status="pending",
            current_step=0,
            total_steps=1,
            created_at=datetime.now(UTC),
        )
        self._tasks_dict[task_id] = task
        return task

    def get_task(self, task_id: str) -> DesktopTaskResponse | None:
        """Retrieves task by ID."""
        return self._tasks_dict.get(task_id)

    def list_tasks(self) -> list[DesktopTaskResponse]:
        """Lists submitted desktop tasks."""
        return list(self._tasks_dict.values())

    def cancel_task(self, task_id: str) -> bool:
        """Cancels a pending or running desktop task."""
        task = self._tasks_dict.get(task_id)
        if not task:
            return False
        task.status = "cancelled"
        task.completed_at = datetime.now(UTC)
        return True

    def get_diagnostics(self) -> DesktopDiagnosticsInfo:
        """Collects comprehensive Windows desktop and COM worker diagnostics."""
        session_info = self.get_session_info()
        worker_health = uia_worker_supervisor.get_health_status()
        active_apps = len(process_discovery_manager.list_running_applications())
        active_windows = len(window_discovery_manager.list_windows(include_invisible=False))

        return DesktopDiagnosticsInfo(
            session=session_info,
            uia_available=True,
            win32_available=True,
            active_worker_threads=worker_health.get("active_workers", 0),
            cached_windows=active_windows,
            registered_applications=active_apps,
            emergency_stop_active=get_emergency_stop_controller().is_emergency_stop_active,
            diagnostic_timestamp=datetime.now(UTC),
        )


desktop_service = DesktopAutomationService()
