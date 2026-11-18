# Windows Capture Engine Specification (Stage 18)

## 1. Capture Providers

The Windows screen capture engine (`app/visual/capture/providers.py`) provides a pluggable provider registry supporting multiple native Windows graphics capture mechanisms:

| Provider | Backend Mechanism | Typical Latency | Best Use Case |
|---|---|---|---|
| **MSS (Direct Grab)** | `user32.GetDC` + `gdi32.BitBlt` via `mss` | 12–20 ms | Multi-monitor desktop capture, primary display scanning |
| **GDI (PrintWindow)** | Win32 `PrintWindow` API with `PW_RENDERFULLCONTENT` | 18–35 ms | Isolated background/occluded native application windows |
| **WGC (Windows Graphics)**| `Windows.Graphics.Capture` WinRT API | 8–15 ms | High-frequency continuous observation & Direct3D apps |
| **DXGI Desktop Duplication**| DirectX GI 1.2 Output Duplication | 5–10 ms | Ultra-low latency GPU-accelerated full desktop capture |

---

## 2. Desktop Attachment & Headless Sandboxing

When running inside background worker processes or sandboxed sessions without an interactive console:
1. `ensure_default_desktop_attached()`: Calls `user32.OpenDesktopW("Default", 0, False, 0x01FF)` and `user32.SetThreadDesktop()` to bind worker threads to the active interactive desktop session.
2. The returned desktop handle is retained for the thread's lifetime to prevent GDI allocation errors.
3. If `BitBlt` fails due to headless virtualization (e.g. CI runners or non-interactive terminals), providers gracefully generate standard display canvases with logged warnings rather than crashing execution.

---

## 3. Preprocessing & Performance Optimization

Raw screenshots (often 4K or multi-monitor resolutions exceeding 7680x2160) are processed by `FramePreprocessor` before being passed to vision models:
- **Aspect-Preserving Downscaling**: Scaled down to max dimension 1600px via high-quality `LANCZOS` resampling.
- **Content Hashing**: SHA-256 hash computed over raw pixel buffers to detect static frames and bypass redundant OCR passes.
- **Frame Differencing**: `calculate_frame_diff_percentage` computes differing pixels between consecutive captures with noise thresholds (>15 luminosity delta).
- **Sensitive Region Masking**: Automatically paints solid black rectangles over detected credit card, token, or password fields.
