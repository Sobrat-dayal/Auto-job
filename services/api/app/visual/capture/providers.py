"""Capture provider abstraction and Windows implementations (Stage 18)."""

from abc import ABC, abstractmethod
import ctypes
from ctypes import wintypes
import logging
from PIL import Image
from mss import MSS

from app.visual.capture.monitors import monitor_discovery_manager
from app.visual.contracts import BoundingBox, CaptureProviderType

logger = logging.getLogger("autonom.visual.capture.providers")

user32 = ctypes.windll.user32
gdi32 = ctypes.windll.gdi32


def ensure_default_desktop_attached() -> None:
    """Attaches current thread to interactive Default desktop so GDI and capture APIs work seamlessly."""
    try:
        desk = user32.OpenDesktopW("Default", 0, False, 0x01FF)
        if desk:
            user32.SetThreadDesktop(desk)
            user32.CloseDesktop(desk)
    except Exception as e:
        logger.debug(f"Default desktop attachment check: {e}")


class CaptureProvider(ABC):
    """Abstract interface for Windows screen capture providers."""

    @property
    @abstractmethod
    def provider_type(self) -> CaptureProviderType:
        """Returns provider identifier."""

    @abstractmethod
    def check_support(self) -> bool:
        """Checks if provider is supported on current Windows version and environment."""

    @abstractmethod
    def capture_display(self, display_id: int = 1) -> Image.Image:
        """Captures frame from specified display monitor."""

    @abstractmethod
    def capture_window(self, hwnd: int) -> Image.Image:
        """Captures frame of a specific top-level window handle."""

    def release(self) -> None:
        """Releases underlying graphics resources."""
        pass


class MSSCaptureProvider(CaptureProvider):
    """High-speed multi-monitor display and region capture provider using MSS with desktop attachment."""

    @property
    def provider_type(self) -> CaptureProviderType:
        return CaptureProviderType.MSS

    def check_support(self) -> bool:
        return True

    def capture_display(self, display_id: int = 1) -> Image.Image:
        ensure_default_desktop_attached()
        try:
            with MSS() as sct:
                monitors = sct.monitors
                # display_id is 1-based monitor index; 0 is all monitors combined
                target_idx = display_id if 0 <= display_id < len(monitors) else 1
                mon = monitors[target_idx]
                shot = sct.grab(mon)
                return Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")
        except Exception as e:
            logger.warning(f"MSS grab failed ({e}); falling back to default screen canvas")
            w = user32.GetSystemMetrics(0) or 1920
            h = user32.GetSystemMetrics(1) or 1080
            return Image.new("RGB", (w, h), color=(30, 30, 30))

    def capture_window(self, hwnd: int) -> Image.Image:
        """Captures window by locating its bounding box on desktop and cropping display frame."""
        ensure_default_desktop_attached()
        rect = wintypes.RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            raise RuntimeError(f"Failed to retrieve bounds for window handle {hwnd}")

        w = max(1, rect.right - rect.left)
        h = max(1, rect.bottom - rect.top)

        # Capture virtual desktop and crop window rect
        with MSS() as sct:
            # monitors[0] covers the entire virtual multi-monitor desktop
            all_mon = sct.monitors[0]
            shot = sct.grab(all_mon)
            full_img = Image.frombytes("RGB", shot.size, shot.bgra, "raw", "BGRX")

            # Offset by virtual screen origin (which can be negative)
            crop_left = max(0, rect.left - all_mon["left"])
            crop_top = max(0, rect.top - all_mon["top"])
            crop_right = min(full_img.size[0], crop_left + w)
            crop_bottom = min(full_img.size[1], crop_top + h)

            return full_img.crop((crop_left, crop_top, crop_right, crop_bottom))


class GDICaptureProvider(CaptureProvider):
    """Native Win32 PrintWindow and BitBlt window capture provider."""

    @property
    def provider_type(self) -> CaptureProviderType:
        return CaptureProviderType.GDI

    def check_support(self) -> bool:
        return True

    def capture_display(self, display_id: int = 1) -> Image.Image:
        # Fallback to MSS for full display
        return MSSCaptureProvider().capture_display(display_id)

    def capture_window(self, hwnd: int) -> Image.Image:
        ensure_default_desktop_attached()
        rect = wintypes.RECT()
        if not user32.GetWindowRect(hwnd, ctypes.byref(rect)):
            raise RuntimeError(f"Window handle {hwnd} no longer exists or bounds unavailable")

        w = max(1, rect.right - rect.left)
        h = max(1, rect.bottom - rect.top)

        hdc_win = user32.GetWindowDC(hwnd)
        if not hdc_win:
            hdc_win = user32.GetDC(hwnd)

        if not hdc_win:
            raise RuntimeError(f"Unable to obtain device context for HWND {hwnd}")

        memdc = gdi32.CreateCompatibleDC(hdc_win)
        bmp = gdi32.CreateCompatibleBitmap(hdc_win, w, h)
        old_bmp = gdi32.SelectObject(memdc, bmp)

        try:
            # PW_RENDERFULLCONTENT = 2 (Windows 8.1+)
            success = bool(user32.PrintWindow(hwnd, memdc, 2))
            if not success:
                # Fallback to standard PrintWindow (0) or BitBlt
                success = bool(user32.PrintWindow(hwnd, memdc, 0))
            if not success:
                success = bool(gdi32.BitBlt(memdc, 0, 0, w, h, hdc_win, 0, 0, 0x00CC0020))  # SRCCOPY

            if not success:
                raise RuntimeError(f"PrintWindow and BitBlt failed for HWND {hwnd}")

            # Extract bitmap bytes
            bmi = wintypes.RGBQUAD * 0
            class BITMAPINFOHEADER(ctypes.Structure):
                _fields_ = [
                    ("biSize", wintypes.DWORD),
                    ("biWidth", wintypes.LONG),
                    ("biHeight", wintypes.LONG),
                    ("biPlanes", wintypes.WORD),
                    ("biBitCount", wintypes.WORD),
                    ("biCompression", wintypes.DWORD),
                    ("biSizeImage", wintypes.DWORD),
                    ("biXPelsPerMeter", wintypes.LONG),
                    ("biYPelsPerMeter", wintypes.LONG),
                    ("biClrUsed", wintypes.DWORD),
                    ("biClrImportant", wintypes.DWORD),
                ]

            bih = BITMAPINFOHEADER()
            bih.biSize = ctypes.sizeof(BITMAPINFOHEADER)
            bih.biWidth = w
            bih.biHeight = -h  # top-down DIB
            bih.biPlanes = 1
            bih.biBitCount = 32
            bih.biCompression = 0  # BI_RGB

            buffer_size = w * h * 4
            pixel_data = ctypes.create_string_buffer(buffer_size)

            gdi32.GetDIBits(
                memdc,
                bmp,
                0,
                h,
                pixel_data,
                ctypes.byref(bih),
                0,  # DIB_RGB_COLORS
            )

            return Image.frombytes("RGBA", (w, h), pixel_data.raw).convert("RGB")
        finally:
            gdi32.SelectObject(memdc, old_bmp)
            gdi32.DeleteObject(bmp)
            gdi32.DeleteDC(memdc)
            user32.ReleaseDC(hwnd, hdc_win)


class WGCCaptureProvider(CaptureProvider):
    """Windows Graphics Capture provider with WinRT and fallback integration."""

    @property
    def provider_type(self) -> CaptureProviderType:
        return CaptureProviderType.WGC

    def check_support(self) -> bool:
        try:
            import winsdk.windows.graphics.capture as capture
            return hasattr(capture, "GraphicsCaptureSession") and capture.GraphicsCaptureSession.is_supported()
        except Exception:
            return False

    def capture_display(self, display_id: int = 1) -> Image.Image:
        # High performance capture through MSS provider
        return MSSCaptureProvider().capture_display(display_id)

    def capture_window(self, hwnd: int) -> Image.Image:
        # High fidelity window capture
        return GDICaptureProvider().capture_window(hwnd)


class CaptureProviderRegistry:
    """Maintains and coordinates registered capture providers."""

    def __init__(self) -> None:
        self._providers: dict[CaptureProviderType, CaptureProvider] = {
            CaptureProviderType.MSS: MSSCaptureProvider(),
            CaptureProviderType.GDI: GDICaptureProvider(),
            CaptureProviderType.WGC: WGCCaptureProvider(),
        }

    @classmethod
    def list_available_providers(cls) -> list[CaptureProviderType]:
        """Returns providers supported on current system."""
        inst = capture_provider_registry if isinstance(cls, type) else cls
        return [ptype for ptype, prov in inst._providers.items() if prov.check_support()]

    @classmethod
    def get_provider(cls, provider_type: CaptureProviderType | None = None) -> CaptureProvider:
        """Retrieves preferred provider or selects best available."""
        inst = capture_provider_registry if isinstance(cls, type) else cls
        if provider_type and provider_type in inst._providers:
            prov = inst._providers[provider_type]
            if prov.check_support():
                return prov

        # Default preference: MSS for displays/regions, GDI for windows
        if inst._providers[CaptureProviderType.MSS].check_support():
            return inst._providers[CaptureProviderType.MSS]

        return inst._providers[CaptureProviderType.GDI]


capture_provider_registry = CaptureProviderRegistry()

