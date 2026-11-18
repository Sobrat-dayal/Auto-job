"""Windows monitor enumeration, DPI discovery, and display geometry (Stage 18)."""

import ctypes
from ctypes import wintypes
import logging
from typing import Any
from app.visual.contracts import BoundingBox, DisplayInfo

logger = logging.getLogger("autonom.visual.capture.monitors")

user32 = ctypes.windll.user32
shcore = getattr(ctypes.windll, "shcore", None)

MONITOR_DEFAULTTONEAREST = 2
MDT_EFFECTIVE_DPI = 0

MONITORENUMPROC = ctypes.WINFUNCTYPE(
    wintypes.BOOL,
    wintypes.HMONITOR,
    wintypes.HDC,
    ctypes.POINTER(wintypes.RECT),
    wintypes.LPARAM,
)


class MONITORINFOEXW(ctypes.Structure):
    _fields_ = [
        ("cbSize", wintypes.DWORD),
        ("rcMonitor", wintypes.RECT),
        ("rcWork", wintypes.RECT),
        ("dwFlags", wintypes.DWORD),
        ("szDevice", wintypes.WCHAR * 32),
    ]


class MonitorDiscoveryManager:
    """Discovers and tracks physical and logical monitors attached to the Windows desktop."""

    def __init__(self) -> None:
        self._user32 = user32
        self._shcore = shcore

    def get_dpi_for_monitor(self, hmonitor: int) -> int:
        """Retrieves effective DPI for a specific monitor handle."""
        if self._shcore and hasattr(self._shcore, "GetDpiForMonitor"):
            dpi_x = wintypes.UINT()
            dpi_y = wintypes.UINT()
            hr = self._shcore.GetDpiForMonitor(hmonitor, MDT_EFFECTIVE_DPI, ctypes.byref(dpi_x), ctypes.byref(dpi_y))
            if hr == 0:
                return int(dpi_x.value)

        # Fallback to system DPI
        if hasattr(self._user32, "GetDpiForSystem"):
            return int(self._user32.GetDpiForSystem())
        return 96

    def enumerate_monitors(self) -> list[DisplayInfo]:
        """Enumerates all active display monitors with physical bounds and DPI."""
        displays: list[DisplayInfo] = []
        mon_idx = 0

        def enum_cb(hmon: int, hdc: int, lprect: Any, lparam: int) -> bool:
            nonlocal mon_idx
            try:
                info = MONITORINFOEXW()
                info.cbSize = ctypes.sizeof(MONITORINFOEXW)
                if self._user32.GetMonitorInfoW(hmon, ctypes.byref(info)):
                    r = info.rcMonitor
                    left = int(r.left)
                    top = int(r.top)
                    width = max(1, int(r.right - r.left))
                    height = max(1, int(r.bottom - r.top))
                    is_primary = bool(info.dwFlags & 1)  # MONITORINFOF_PRIMARY = 1
                    dev_name = str(info.szDevice).strip() or f"Display {mon_idx + 1}"

                    dpi = self.get_dpi_for_monitor(hmon)
                    scale_factor = round(dpi / 96.0, 2)
                    orientation = "landscape" if width >= height else "portrait"

                    displays.append(
                        DisplayInfo(
                            id=mon_idx + 1,
                            name=dev_name,
                            left=left,
                            top=top,
                            width=width,
                            height=height,
                            is_primary=is_primary,
                            dpi=dpi,
                            scale_factor=scale_factor,
                            orientation=orientation,
                        )
                    )
                    mon_idx += 1
            except Exception as e:
                logger.debug(f"Error inspecting monitor {hmon}: {e}")
            return True

        self._user32.EnumDisplayMonitors(0, 0, MONITORENUMPROC(enum_cb), 0)

        # Fallback if EnumDisplayMonitors returned empty
        if not displays:
            sw = self._user32.GetSystemMetrics(0) or 1920
            sh = self._user32.GetSystemMetrics(1) or 1080
            displays.append(
                DisplayInfo(
                    id=1,
                    name="Default Display",
                    left=0,
                    top=0,
                    width=sw,
                    height=sh,
                    is_primary=True,
                    dpi=96,
                    scale_factor=1.0,
                    orientation="landscape",
                )
            )

        return displays

    def get_virtual_desktop_bounds(self) -> BoundingBox:
        """Returns the aggregate bounding box covering all active displays (supports negative coordinates)."""
        left = self._user32.GetSystemMetrics(76)  # SM_XVIRTUALSCREEN
        top = self._user32.GetSystemMetrics(77)   # SM_YVIRTUALSCREEN
        width = self._user32.GetSystemMetrics(78) # SM_CXVIRTUALSCREEN
        height = self._user32.GetSystemMetrics(79) # SM_CYVIRTUALSCREEN

        if width <= 0 or height <= 0:
            displays = self.enumerate_monitors()
            min_x = min(d.left for d in displays)
            min_y = min(d.top for d in displays)
            max_r = max(d.left + d.width for d in displays)
            max_b = max(d.top + d.height for d in displays)
            return BoundingBox(left=min_x, top=min_y, width=max_r - min_x, height=max_b - min_y)

        return BoundingBox(left=left, top=top, width=width, height=height)

    @classmethod
    def discover_monitors(cls) -> list[DisplayInfo]:
        """Classmethod returning discovered displays via singleton."""
        return monitor_discovery_manager.enumerate_monitors()

    @classmethod
    def get_virtual_desktop_rect(cls) -> dict[str, int]:
        """Classmethod returning virtual desktop bounding rect dict."""
        b = monitor_discovery_manager.get_virtual_desktop_bounds()
        return {"left": b.left, "top": b.top, "width": b.width, "height": b.height}


monitor_discovery_manager = MonitorDiscoveryManager()

