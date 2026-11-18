"""Win32 compatibility adapter for legacy Windows controls (Stage 17)."""

import ctypes
from ctypes import wintypes
import logging

logger = logging.getLogger("autonom.computer.win32.adapter")

user32 = ctypes.windll.user32

# Standard Win32 Window Messages
WM_GETTEXT = 0x000D
WM_SETTEXT = 0x000C
WM_COMMAND = 0x0111
BM_CLICK = 0x00F5
CB_GETCOUNT = 0x0146
CB_SETCURSEL = 0x014E
CB_GETCURSEL = 0x0147
EM_SETSEL = 0x00B1
EM_REPLACESEL = 0x00C2


class Win32CompatibilityAdapter:
    """Provides fallback message-based interactions for legacy standard Win32 controls."""

    @staticmethod
    def get_text(hwnd: int) -> str:
        """Reads text from a legacy control using WM_GETTEXT."""
        if not user32.IsWindow(hwnd):
            return ""
        length = user32.SendMessageW(hwnd, 0x000E, 0, 0)  # WM_GETTEXTLENGTH
        if length <= 0:
            return ""
        buf = ctypes.create_unicode_buffer(length + 1)
        user32.SendMessageW(hwnd, WM_GETTEXT, length + 1, ctypes.byref(buf))
        return buf.value

    @staticmethod
    def set_text(hwnd: int, text: str) -> bool:
        """Sets the text of a legacy control using WM_SETTEXT."""
        if not user32.IsWindow(hwnd):
            return False
        buf = ctypes.create_unicode_buffer(text)
        res = user32.SendMessageW(hwnd, WM_SETTEXT, 0, ctypes.byref(buf))
        return bool(res)

    @staticmethod
    def click_button(hwnd: int) -> bool:
        """Clicks a legacy button control using BM_CLICK."""
        if not user32.IsWindow(hwnd):
            return False
        user32.SendMessageW(hwnd, BM_CLICK, 0, 0)
        return True

    @staticmethod
    def select_combobox_index(hwnd: int, index: int) -> bool:
        """Selects an item index in a legacy combobox using CB_SETCURSEL."""
        if not user32.IsWindow(hwnd):
            return False
        res = user32.SendMessageW(hwnd, CB_SETCURSEL, index, 0)
        return res != -1


win32_adapter = Win32CompatibilityAdapter()
