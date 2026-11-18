"""Windows interactive desktop session detection (Stage 17)."""

import ctypes
from ctypes import wintypes
from datetime import UTC, datetime
import logging
import os
import psutil

from app.computer.contracts import DesktopSessionInfo, DesktopSessionState

logger = logging.getLogger("autonom.computer.windows.sessions")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32


class DesktopSessionManager:
    """Detects and monitors the active Windows interactive desktop session."""

    def __init__(self) -> None:
        self._user32 = user32
        self._kernel32 = kernel32

    def get_session_info(self) -> DesktopSessionInfo:
        """Returns current Windows session telemetry, lock state, and resolution."""
        pid = os.getpid()
        session_id = ctypes.c_ulong(1)
        try:
            self._kernel32.ProcessIdToSessionId(pid, ctypes.byref(session_id))
            wts_id = int(session_id.value)
        except Exception:
            wts_id = 1

        # Check screen resolution
        try:
            width = self._user32.GetSystemMetrics(0)  # SM_CXSCREEN
            height = self._user32.GetSystemMetrics(1)  # SM_CYSCREEN
            resolution = f"{width}x{height}" if width and height else "1920x1080"
        except Exception:
            resolution = "1920x1080"

        # Check user name
        try:
            user_name = psutil.Process(pid).username()
        except Exception:
            user_name = os.getenv("USERNAME", "User")

        # Check lock / interactive desktop status
        is_locked = False
        is_interactive = True
        status = DesktopSessionState.ACTIVE

        try:
            # OpenInputDesktop returns NULL or fails with ERROR_ACCESS_DENIED if locked or secure desktop active
            desk = self._user32.OpenInputDesktop(0, False, 0x0100)  # DESKTOP_ENUMERATE
            if not desk:
                err = self._kernel32.GetLastError()
                # 5 = ERROR_ACCESS_DENIED (Desktop locked or secure UAC prompt)
                if err == 5:
                    is_locked = True
                    status = DesktopSessionState.LOCKED
                else:
                    status = DesktopSessionState.UNAVAILABLE
                    is_interactive = False
            else:
                self._user32.CloseDesktop(desk)
        except Exception as e:
            logger.debug(f"OpenInputDesktop check: {e}")

        # Check desktop name
        desktop_name = "Default"
        try:
            thread_desk = self._user32.GetThreadDesktop(self._kernel32.GetCurrentThreadId())
            if thread_desk:
                buf = ctypes.create_unicode_buffer(256)
                needed = ctypes.c_ulong()
                if self._user32.GetUserObjectInformationW(thread_desk, 2, buf, 256, ctypes.byref(needed)):
                    desktop_name = buf.value
        except Exception:
            pass

        return DesktopSessionInfo(
            wts_session_id=wts_id,
            status=status,
            desktop_name=desktop_name,
            user_name=user_name,
            resolution=resolution,
            is_interactive=is_interactive,
            is_locked=is_locked,
            last_active_at=datetime.now(UTC),
        )


session_manager = DesktopSessionManager()
