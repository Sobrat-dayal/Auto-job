"""Native Windows top-level window discovery and validation (Stage 17)."""

import ctypes
from ctypes import wintypes
from datetime import UTC, datetime
import logging
import psutil

from app.computer.contracts import WindowBounds, WindowInfo

logger = logging.getLogger("autonom.computer.windows.windows")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

WNDENUMPROC = ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)


class WindowDiscoveryManager:
    """Discovers, tracks, and validates native Windows top-level windows."""

    # Internal Windows shell classes to filter out of normal app lists
    IGNORED_CLASSES = {
        "Progman",
        "WorkerW",
        "Shell_TrayWnd",
        "Shell_SecondaryTrayWnd",
        "ThumbnailDeviceHelperWnd",
        "ForegroundStaging",
    }

    def __init__(self) -> None:
        self._user32 = user32

    def list_windows(self, include_invisible: bool = False) -> list[WindowInfo]:
        """Enumerates top-level windows on the interactive Default desktop."""
        windows: list[WindowInfo] = []

        # Open interactive Default desktop
        desktop = self._user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if not desktop:
            logger.warning("Unable to open Default desktop; falling back to thread desktop")
            desktop = self._user32.GetThreadDesktop(kernel32.GetCurrentThreadId())

        fg_hwnd = self._user32.GetForegroundWindow()

        def enum_cb(hwnd: int, lparam: int) -> bool:
            try:
                is_visible = bool(self._user32.IsWindowVisible(hwnd))
                if not is_visible and not include_invisible:
                    return True

                # Read title
                length = self._user32.GetWindowTextLengthW(hwnd)
                if length == 0 and not include_invisible:
                    return True

                title_buf = ctypes.create_unicode_buffer(length + 1)
                self._user32.GetWindowTextW(hwnd, title_buf, length + 1)
                title = title_buf.value.strip()

                # Read class name
                class_buf = ctypes.create_unicode_buffer(256)
                self._user32.GetClassNameW(hwnd, class_buf, 256)
                win_class = class_buf.value.strip()

                if win_class in self.IGNORED_CLASSES:
                    return True

                # Process ID
                pid = wintypes.DWORD()
                self._user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
                p_id = int(pid.value)

                # Process Name
                try:
                    proc_name = psutil.Process(p_id).name()
                except Exception:
                    proc_name = "unknown.exe"

                # State
                is_enabled = bool(self._user32.IsWindowEnabled(hwnd))
                is_minimized = bool(self._user32.IsIconic(hwnd))
                is_maximized = bool(self._user32.IsZoomed(hwnd))
                is_foreground = (hwnd == fg_hwnd)

                # Bounds
                rect = wintypes.RECT()
                self._user32.GetWindowRect(hwnd, ctypes.byref(rect))
                bounds = WindowBounds(
                    left=rect.left,
                    top=rect.top,
                    right=rect.right,
                    bottom=rect.bottom,
                    width=max(0, rect.right - rect.left),
                    height=max(0, rect.bottom - rect.top),
                )

                window_ref = f"win_{hwnd}_{p_id}"
                windows.append(
                    WindowInfo(
                        window_ref=window_ref,
                        hwnd=hwnd,
                        pid=p_id,
                        process_name=proc_name,
                        title=title or f"[{win_class}]",
                        window_class=win_class,
                        is_visible=is_visible,
                        is_enabled=is_enabled,
                        is_foreground=is_foreground,
                        is_minimized=is_minimized,
                        is_maximized=is_maximized,
                        bounds=bounds,
                        created_at=datetime.now(UTC),
                    )
                )
            except Exception as e:
                logger.debug(f"Error inspecting window {hwnd}: {e}")
            return True

        try:
            self._user32.EnumDesktopWindows(desktop, WNDENUMPROC(enum_cb), 0)
        finally:
            if desktop and desktop != self._user32.GetThreadDesktop(kernel32.GetCurrentThreadId()):
                self._user32.CloseDesktop(desktop)

        return windows

    def validate_window_ref(self, window_ref: str) -> WindowInfo | None:
        """Validates that a window_ref still exists, is a valid window, and belongs to the expected PID."""
        try:
            parts = window_ref.split("_")
            if len(parts) != 3 or parts[0] != "win":
                return None
            hwnd = int(parts[1])
            expected_pid = int(parts[2])
        except (ValueError, IndexError):
            return None

        # Attach to Default desktop if needed for cross-desktop validation
        desktop = self._user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if desktop:
            try:
                self._user32.SetThreadDesktop(desktop)
            except Exception:
                pass

        try:
            # Verify HWND exists
            if not self._user32.IsWindow(hwnd):
                logger.warning(f"Window handle {hwnd} no longer exists (stale window_ref: {window_ref})")
                return None

            # Verify PID has not changed (preventing HWND recycling attack)
            actual_pid = wintypes.DWORD()
            self._user32.GetWindowThreadProcessId(hwnd, ctypes.byref(actual_pid))
            if int(actual_pid.value) != expected_pid:
                logger.warning(
                    f"HWND {hwnd} has been recycled: expected PID {expected_pid}, actual PID {actual_pid.value}"
                )
                return None
        finally:
            if desktop:
                try:
                    self._user32.CloseDesktop(desktop)
                except Exception:
                    pass

        # Fetch current metadata
        all_windows = self.list_windows(include_invisible=True)
        for w in all_windows:
            if w.window_ref == window_ref:
                return w

        return None

    def find_window_by_ref(self, window_ref: str) -> WindowInfo | None:
        """Finds window by validated reference."""
        return self.validate_window_ref(window_ref)


window_discovery_manager = WindowDiscoveryManager()
