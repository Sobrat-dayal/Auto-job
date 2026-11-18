# Stage 19: Interaction Adapters Specification

## 1. Overview & Interface Protocol

All computer interaction methods in AUTONOM implement the `InteractionAdapter` protocol (`services/api/app/hybrid/adapters/base.py`), exposing a normalized four-phase interface:

```python
class InteractionAdapter(Protocol):
    method: InteractionMethod

    async def probe(self, target: InteractionTarget) -> CapabilityProbe:
        """Evaluate whether this adapter can interact with the given target."""
        ...

    async def observe(self, request: ObservationRequest) -> InteractionObservation:
        """Capture structural and textual state of the target."""
        ...

    async def execute(self, action: InteractionAction) -> InteractionResult:
        """Execute an action against the target."""
        ...

    async def verify(self, action: InteractionAction, result: InteractionResult) -> InteractionResult:
        """Verify the post-action state mutation."""
        ...
```

---

## 2. Adapter Implementations

### 2.1. BrowserDOMAdapter (`adapters/browser.py`)
- **Backend Service:** Bridges Stage 16 `BrowserService` and active Playwright sessions.
- **Surface Target:** `SurfaceType.BROWSER_DOM` or `SurfaceType.EMBEDDED_WEBVIEW`.
- **Intrusiveness:** Zero (executes inside Chromium rendering engine without moving the physical OS cursor).
- **Supported Actions:** `click`, `double_click`, `enter_text`, `navigate`, `scroll`, `select_option`, `submit`, `inspect`.
- **Relative Cost:** 1 / 5 (Lowest latency, highly reliable DOM selectors and CSS paths).
- **Verification:** Evaluates DOM attribute changes, URL navigation, and element removal.

### 2.2. WindowsUIAAdapter (`adapters/uia.py`)
- **Backend Service:** Bridges Stage 17 `DesktopAutomationService` via Microsoft UI Automation COM interfaces.
- **Surface Target:** `SurfaceType.NATIVE_UIA`.
- **Intrusiveness:** Low (prefers UIA control patterns such as `InvokePattern`, `ValuePattern.SetValue`, and `ExpandCollapsePattern`).
- **Supported Actions:** `click`, `double_click`, `enter_text`, `scroll`, `inspect`, `key_press`.
- **Relative Cost:** 2 / 5 (Fast direct COM calls, rich accessibility tree structure).
- **Verification:** Reads updated element Value, ToggleState, or window focus states.

### 2.3. Win32Adapter (`adapters/win32.py`)
- **Backend Service:** Windows User32 HWND messaging (`PostMessage`, `SendMessage`, `WM_COMMAND`, `WM_SETTEXT`, `WM_LBUTTONDOWN`).
- **Surface Target:** `SurfaceType.NATIVE_WIN32`.
- **Intrusiveness:** Minimal for background message queues; higher if requiring window activation.
- **Supported Actions:** `click`, `enter_text`, `key_press`, `hotkey`, `inspect`.
- **Relative Cost:** 2 / 5 (Direct kernel calls, effective for legacy dialogs where UIA elements fail).
- **Verification:** Inspects window text, control state flags, or child window existence.

### 2.4. VisualAdapter (`adapters/visual.py`)
- **Backend Service:** Bridges Stage 18 `VisualComputerService` (MSS/GDI screen capture, offline Windows Media OCR, and visual grounding).
- **Surface Target:** `SurfaceType.CUSTOM_RENDERED`, `SurfaceType.UNKNOWN`, or fallback for any failed structural adapter.
- **Intrusiveness:** High (requires exclusive foreground focus and coordinates-based `SendInput` mouse/keyboard events).
- **Supported Actions:** `click`, `double_click`, `right_click`, `enter_text`, `key_press`, `hotkey`, `scroll`.
- **Relative Cost:** 4 / 5 (Resource-intensive due to full screen capture, image processing, OCR, and coordinate mapping).
- **Verification:** Computes visual difference percentage between pre-action and post-action display frames.

---

## 3. Dynamic Adapter Registry (`adapters/registry.py`)

The `InteractionAdapterRegistry` manages adapter lifecycles, health states, and discovery:
- **`register(adapter)`**: Binds adapter instance to its `InteractionMethod` key.
- **`probe_all(target)`**: Concurrently queries all registered adapters using `asyncio.gather(return_exceptions=True)`, returning a dictionary of `CapabilityProbe` records.
- **`record_execution(method, success, latency_ms, error)`**: Updates runtime telemetry in `MethodHealthTracker`.
