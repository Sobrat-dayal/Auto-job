"""Windows state management: minimize, maximize, restore, close (Stage 17)."""

import ctypes
import logging

from app.computer.contracts import WindowBounds, WindowInfo, WindowManageAction
from app.computer.windows.focus import focus_manager
from app.computer.windows.windows import window_discovery_manager

logger = logging.getLogger("autonom.computer.windows.management")

user32 = ctypes.windll.user32


class WindowStateManager:
    """Performs state management operations on validated Windows applications."""

    SW_HIDE = 0
    SW_NORMAL = 1
    SW_MAXIMIZE = 3
    SW_SHOW = 5
    SW_MINIMIZE = 6
    SW_RESTORE = 9
    WM_CLOSE = 0x0010

    @classmethod
    def execute_window_action(cls, window_ref: str, action: WindowManageAction) -> bool:
        """Executes a window state modification action on a verified window."""
        win = window_discovery_manager.validate_window_ref(window_ref)
        if not win:
            logger.warning(f"Window reference invalid or window closed: {window_ref}")
            return False

        hwnd = win.hwnd

        if action == WindowManageAction.ACTIVATE:
            return focus_manager.activate_window(hwnd)

        elif action == WindowManageAction.MINIMIZE:
            res = bool(user32.ShowWindow(hwnd, cls.SW_MINIMIZE))
            return res or bool(user32.IsIconic(hwnd))

        elif action == WindowManageAction.MAXIMIZE:
            res = bool(user32.ShowWindow(hwnd, cls.SW_MAXIMIZE))
            return res or bool(user32.IsZoomed(hwnd))

        elif action == WindowManageAction.RESTORE:
            res = bool(user32.ShowWindow(hwnd, cls.SW_RESTORE))
            return res or (not user32.IsIconic(hwnd) and not user32.IsZoomed(hwnd))

        elif action == WindowManageAction.CLOSE:
            # Graceful close via WM_CLOSE (does not force-kill the process)
            user32.PostMessageW(hwnd, cls.WM_CLOSE, 0, 0)
            return True

        return False


window_state_manager = WindowStateManager()
