"""Focused, authorized keyboard interaction restricted to verified target window (Stage 17)."""

import ctypes
from ctypes import wintypes
import logging
import time

from app.computer.windows.focus import focus_manager

logger = logging.getLogger("autonom.computer.actions.keyboard")

user32 = ctypes.windll.user32

# Win32 SendInput constants
INPUT_KEYBOARD = 1
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

VK_MAPPING = {
    "enter": 0x0D,
    "return": 0x0D,
    "tab": 0x09,
    "esc": 0x1B,
    "escape": 0x1B,
    "space": 0x20,
    "backspace": 0x08,
    "delete": 0x2E,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "home": 0x24,
    "end": 0x23,
    "ctrl": 0x11,
    "shift": 0x10,
    "alt": 0x12,
}


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_ulonglong),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [("ki", KEYBDINPUT)]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", INPUT_UNION),
    ]


class FocusedKeyboardAdapter:
    """Sends keystrokes exclusively to a verified, foreground-focused target window."""

    @classmethod
    def send_key_to_window(
        cls,
        target_hwnd: int,
        key_name: str,
        modifiers: list[str] | None = None,
    ) -> bool:
        """Sends a single keypress (with optional modifiers) ONLY if the target window is in the foreground."""
        if not user32.IsWindow(target_hwnd):
            logger.error(f"Cannot send key: HWND {target_hwnd} does not exist")
            return False

        # Verify foreground state
        if not focus_manager.is_foreground_window(target_hwnd):
            # Attempt to bring to front
            focus_manager.activate_window(target_hwnd)
            time.sleep(0.05)
            if not focus_manager.is_foreground_window(target_hwnd):
                logger.warning(f"Aborting keystroke: HWND {target_hwnd} is not foreground window")
                return False

        vk = VK_MAPPING.get(key_name.lower())
        if not vk:
            logger.warning(f"Unsupported key name: {key_name}")
            return False

        mod_vks = [VK_MAPPING[m.lower()] for m in (modifiers or []) if m.lower() in VK_MAPPING]

        inputs = []

        # Press modifiers down
        for mvk in mod_vks:
            inp = INPUT(type=INPUT_KEYBOARD)
            inp.u.ki = KEYBDINPUT(wVk=mvk, wScan=0, dwFlags=0, time=0, dwExtraInfo=0)
            inputs.append(inp)

        # Press main key down & up
        inp_down = INPUT(type=INPUT_KEYBOARD)
        inp_down.u.ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=0, time=0, dwExtraInfo=0)
        inputs.append(inp_down)

        inp_up = INPUT(type=INPUT_KEYBOARD)
        inp_up.u.ki = KEYBDINPUT(wVk=vk, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=0)
        inputs.append(inp_up)

        # Release modifiers
        for mvk in reversed(mod_vks):
            inp = INPUT(type=INPUT_KEYBOARD)
            inp.u.ki = KEYBDINPUT(wVk=mvk, wScan=0, dwFlags=KEYEVENTF_KEYUP, time=0, dwExtraInfo=0)
            inputs.append(inp)

        input_array = (INPUT * len(inputs))(*inputs)
        sent = user32.SendInput(len(inputs), input_array, ctypes.sizeof(INPUT))
        return sent == len(inputs)

    @classmethod
    def send_text_to_window(cls, target_hwnd: int, text: str) -> bool:
        """Sends unicode text input ONLY if target window is verified in foreground."""
        if not focus_manager.is_foreground_window(target_hwnd):
            focus_manager.activate_window(target_hwnd)
            time.sleep(0.05)
            if not focus_manager.is_foreground_window(target_hwnd):
                return False

        inputs = []
        for char in text:
            # Down
            inp_down = INPUT(type=INPUT_KEYBOARD)
            inp_down.u.ki = KEYBDINPUT(
                wVk=0,
                wScan=ord(char),
                dwFlags=KEYEVENTF_UNICODE,
                time=0,
                dwExtraInfo=0,
            )
            inputs.append(inp_down)

            # Up
            inp_up = INPUT(type=INPUT_KEYBOARD)
            inp_up.u.ki = KEYBDINPUT(
                wVk=0,
                wScan=ord(char),
                dwFlags=KEYEVENTF_UNICODE | KEYEVENTF_KEYUP,
                time=0,
                dwExtraInfo=0,
            )
            inputs.append(inp_up)

        input_array = (INPUT * len(inputs))(*inputs)
        sent = user32.SendInput(len(inputs), input_array, ctypes.sizeof(INPUT))
        return sent == len(inputs)


focused_keyboard = FocusedKeyboardAdapter()
