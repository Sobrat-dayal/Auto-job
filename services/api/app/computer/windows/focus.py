"""Windows focus and foreground management (Stage 17)."""

import ctypes
from ctypes import wintypes
import logging
import time

logger = logging.getLogger("autonom.computer.windows.focus")

user32 = ctypes.windll.user32


class FocusManager:
    """Manages window foreground activation and focus verification."""

    SW_RESTORE = 9
    SW_SHOW = 5

    @classmethod
    def activate_window(cls, hwnd: int) -> bool:
        """Safely brings target window to foreground and restores if minimized."""
        if not user32.IsWindow(hwnd):
            return False

        # If minimized, restore first
        if user32.IsIconic(hwnd):
            user32.ShowWindow(hwnd, cls.SW_RESTORE)
            time.sleep(0.05)

        user32.ShowWindow(hwnd, cls.SW_SHOW)
        user32.BringWindowToTop(hwnd)
        res = bool(user32.SetForegroundWindow(hwnd))

        # Give the window manager a moment to update foreground
        time.sleep(0.05)
        current_fg = user32.GetForegroundWindow()
        return current_fg == hwnd or res

    @classmethod
    def get_foreground_hwnd(cls) -> int:
        """Returns HWND of the currently focused foreground window."""
        return int(user32.GetForegroundWindow())

    @classmethod
    def is_foreground_window(cls, hwnd: int) -> bool:
        """Checks if the given HWND is the current foreground window."""
        return cls.get_foreground_hwnd() == hwnd


focus_manager = FocusManager()
