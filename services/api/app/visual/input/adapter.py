"""Native Windows SendInput adapter for mouse, keyboard, scroll, and drag (Stage 18)."""

import asyncio
import ctypes
from ctypes import wintypes
import logging
import time

from app.computer.windows.sessions import session_manager
from app.security.authorization.emergency import get_emergency_stop_controller
from app.visual.capture.monitors import monitor_discovery_manager
from app.visual.contracts import Point2D
from app.visual.grounding.coordinates import coordinate_transformer

logger = logging.getLogger("autonom.visual.input.adapter")

user32 = ctypes.windll.user32

# Input Types
INPUT_MOUSE = 0
INPUT_KEYBOARD = 1

# Mouse Flags
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040
MOUSEEVENTF_WHEEL = 0x0800
MOUSEEVENTF_ABSOLUTE = 0x8000
MOUSEEVENTF_VIRTUALDESK = 0x4000

# Keyboard Flags
KEYEVENTF_KEYUP = 0x0002
KEYEVENTF_UNICODE = 0x0004

# Virtual Key Mapping
VK_MAPPING = {
    "enter": 0x0D,
    "return": 0x0D,
    "tab": 0x09,
    "esc": 0x1B,
    "escape": 0x1B,
    "backspace": 0x08,
    "space": 0x20,
    "up": 0x26,
    "down": 0x28,
    "left": 0x25,
    "right": 0x27,
    "home": 0x24,
    "end": 0x23,
    "delete": 0x2E,
}


class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", wintypes.LONG),
        ("dy", wintypes.LONG),
        ("mouseData", wintypes.DWORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", wintypes.WORD),
        ("wScan", wintypes.WORD),
        ("dwFlags", wintypes.DWORD),
        ("time", wintypes.DWORD),
        ("dwExtraInfo", ctypes.c_size_t),
    ]


class HARDWAREINPUT(ctypes.Structure):
    _fields_ = [
        ("uMsg", wintypes.DWORD),
        ("wParamL", wintypes.WORD),
        ("wParamH", wintypes.WORD),
    ]


class INPUT_UNION(ctypes.Union):
    _fields_ = [
        ("mi", MOUSEINPUT),
        ("ki", KEYBDINPUT),
        ("hi", HARDWAREINPUT),
    ]


class INPUT(ctypes.Structure):
    _fields_ = [
        ("type", wintypes.DWORD),
        ("u", INPUT_UNION),
    ]


class WindowsInputAdapter:
    """Dispatches mouse movements, clicks, keystrokes, and text safely via Windows SendInput."""

    def __init__(self) -> None:
        self._user32 = user32

    def _assert_safety_boundaries(self) -> None:
        """Enforces fail-closed Emergency Stop and session lock guardrails."""
        if get_emergency_stop_controller().is_emergency_stop_active:
            raise PermissionError("Input blocked: global Emergency Stop is active")

        session_info = session_manager.get_session_info()
        if session_info.is_locked:
            raise PermissionError("Input blocked: Windows workstation is locked")

        if not session_info.is_interactive:
            raise PermissionError("Input blocked: session is non-interactive")

    def _send_inputs(self, inputs: list[INPUT]) -> int:
        """Helper to invoke SendInput with structured array."""
        self._assert_safety_boundaries()
        count = len(inputs)
        arr = (INPUT * count)(*inputs)
        return int(self._user32.SendInput(count, arr, ctypes.sizeof(INPUT)))

    def move_cursor(self, desktop_point: Point2D) -> bool:
        """Moves cursor to target physical desktop coordinates."""
        v_bounds = monitor_discovery_manager.get_virtual_desktop_bounds()
        norm_x, norm_y = coordinate_transformer.desktop_to_normalized_input(desktop_point, v_bounds)

        inp = INPUT()
        inp.type = INPUT_MOUSE
        inp.u.mi.dx = norm_x
        inp.u.mi.dy = norm_y
        inp.u.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK

        return self._send_inputs([inp]) == 1

    def click(self, desktop_point: Point2D | None = None) -> bool:
        """Performs left button down and up at specified or current coordinates."""
        if desktop_point:
            self.move_cursor(desktop_point)
            time.sleep(0.02)

        down = INPUT(type=INPUT_MOUSE)
        down.u.mi.dwFlags = MOUSEEVENTF_LEFTDOWN

        up = INPUT(type=INPUT_MOUSE)
        up.u.mi.dwFlags = MOUSEEVENTF_LEFTUP

        return self._send_inputs([down, up]) == 2

    def double_click(self, desktop_point: Point2D | None = None) -> bool:
        """Executes double click sequence with standard Windows timing."""
        res1 = self.click(desktop_point)
        time.sleep(0.08)
        res2 = self.click()
        return res1 and res2

    def right_click(self, desktop_point: Point2D | None = None) -> bool:
        """Performs right click sequence."""
        if desktop_point:
            self.move_cursor(desktop_point)
            time.sleep(0.02)

        down = INPUT(type=INPUT_MOUSE)
        down.u.mi.dwFlags = MOUSEEVENTF_RIGHTDOWN

        up = INPUT(type=INPUT_MOUSE)
        up.u.mi.dwFlags = MOUSEEVENTF_RIGHTUP

        return self._send_inputs([down, up]) == 2

    def scroll(self, delta: int = 120) -> bool:
        """Sends mouse wheel scroll event."""
        inp = INPUT(type=INPUT_MOUSE)
        inp.u.mi.dwFlags = MOUSEEVENTF_WHEEL
        inp.u.mi.mouseData = delta  # 120 per standard wheel notch

        return self._send_inputs([inp]) == 1

    def drag(self, start: Point2D, end: Point2D, steps: int = 10) -> bool:
        """Smoothly moves cursor while holding left mouse button, guaranteed release on exit."""
        v_bounds = monitor_discovery_manager.get_virtual_desktop_bounds()

        # 1. Move to start and press down
        self.move_cursor(start)
        time.sleep(0.02)
        down = INPUT(type=INPUT_MOUSE)
        down.u.mi.dwFlags = MOUSEEVENTF_LEFTDOWN
        self._send_inputs([down])

        try:
            # 2. Interpolate motion steps
            for i in range(1, steps + 1):
                cur_x = int(start.x + (end.x - start.x) * (i / float(steps)))
                cur_y = int(start.y + (end.y - start.y) * (i / float(steps)))
                self.move_cursor(Point2D(x=cur_x, y=cur_y))
                time.sleep(0.015)
            return True
        finally:
            # 3. Always release mouse button even on error
            up = INPUT(type=INPUT_MOUSE)
            up.u.mi.dwFlags = MOUSEEVENTF_LEFTUP
            self._send_inputs([up])

    def press_key(self, key_name: str) -> bool:
        """Sends single virtual key press and release."""
        vk_code = VK_MAPPING.get(key_name.lower())
        if not vk_code:
            logger.warning(f"Unmapped virtual key: {key_name}")
            return False

        down = INPUT(type=INPUT_KEYBOARD)
        down.u.ki.wVk = vk_code

        up = INPUT(type=INPUT_KEYBOARD)
        up.u.ki.wVk = vk_code
        up.u.ki.dwFlags = KEYEVENTF_KEYUP

        return self._send_inputs([down, up]) == 2

    def enter_text(self, text: str) -> bool:
        """Types unicode string into active focused control."""
        inputs: list[INPUT] = []
        for ch in text:
            code = ord(ch)
            down = INPUT(type=INPUT_KEYBOARD)
            down.u.ki.wScan = code
            down.u.ki.dwFlags = KEYEVENTF_UNICODE

            up = INPUT(type=INPUT_KEYBOARD)
            up.u.ki.wScan = code
            up.u.ki.dwFlags = KEYEVENTF_UNICODE | KEYEVENTF_KEYUP

            inputs.extend([down, up])

        return self._send_inputs(inputs) == len(inputs)


windows_input_adapter = WindowsInputAdapter()
