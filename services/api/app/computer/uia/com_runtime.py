"""COM runtime, MTA threading, and UI Automation initialization (Stage 17)."""

import ctypes
from ctypes import wintypes
import logging
import threading
from typing import Any

import comtypes
import comtypes.client

logger = logging.getLogger("autonom.computer.uia.com_runtime")

user32 = ctypes.windll.user32
kernel32 = ctypes.windll.kernel32

# Cache UIAutomation module load
_UIA_INITIALIZED = False


def ensure_uia_module_loaded() -> None:
    """Ensures UIAutomationCore.dll type library is generated and loaded."""
    global _UIA_INITIALIZED
    if not _UIA_INITIALIZED:
        try:
            comtypes.client.GetModule("UIAutomationCore.dll")
            _UIA_INITIALIZED = True
        except Exception as e:
            logger.error(f"Failed to load UIAutomationCore.dll: {e}")
            raise


class COMWorkerContext:
    """Context manager for dedicated worker threads executing UIA COM calls."""

    def __init__(self, target_desktop: str = "Default") -> None:
        self.target_desktop = target_desktop
        self.desktop_handle = None
        self.com_initialized = False

    def __enter__(self) -> "COMWorkerContext":
        # Ensure thread desktop is set to the interactive Default desktop if needed
        try:
            self.desktop_handle = user32.OpenDesktopW(self.target_desktop, 0, False, 0x01FF)
            if self.desktop_handle:
                user32.SetThreadDesktop(self.desktop_handle)
        except Exception as e:
            logger.debug(f"Desktop attach notice: {e}")

        # Initialize COM in Multi-Threaded Apartment (MTA) mode
        try:
            comtypes.CoInitializeEx(comtypes.COINIT_MULTITHREADED)
            self.com_initialized = True
        except OSError as e:
            # RPC_E_CHANGED_MODE (-2147417850) if already initialized on thread
            if e.winerror == -2147417850:
                self.com_initialized = False
            else:
                logger.warning(f"CoInitializeEx error: {e}")

        ensure_uia_module_loaded()
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        if self.com_initialized:
            try:
                comtypes.CoUninitialize()
            except Exception:
                pass

        if self.desktop_handle:
            try:
                curr_desk = user32.GetThreadDesktop(kernel32.GetCurrentThreadId())
                if self.desktop_handle != curr_desk:
                    user32.CloseDesktop(self.desktop_handle)
            except Exception:
                pass


def create_uia_client():
    """Instantiates a thread-safe IUIAutomation client COM object."""
    from comtypes.gen.UIAutomationClient import CUIAutomation, IUIAutomation
    return comtypes.client.CreateObject(CUIAutomation, interface=IUIAutomation)
