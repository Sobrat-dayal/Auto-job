# Stage 19: Unified Target Identity & Surface Classification

## 1. Overview & Problem Definition

Desktop automation systems fail unpredictably when targets are addressed using ambiguous or stale references. Common failure modes include:
1. **Recycled Window Handles (HWNDs):** In Win32, when an application closes, Windows reassigns its numeric HWND to newly opened windows. Operating on an HWND without verifying its owning PID can result in typing or clicking inside the wrong application.
2. **Ambiguous DOM Selectors:** Dynamically generated single-page web applications change IDs and class names across sessions.
3. **Cross-Modality Incompatibilities:** Passing an HWND to a browser agent or a DOM CSS selector to UI Automation results in immediate crashes.

Stage 19 solves this with a normalized `InteractionTarget` contract, rigorous identity validation, and an automatic `SurfaceClassifier`.

---

## 2. InteractionTarget Contract

```python
class InteractionTarget(BaseModel):
    target_id: str = Field(default_factory=lambda: f"tgt_{uuid.uuid4().hex[:12]}")
    target_type: TargetType
    surface_type: SurfaceType

    # Web Identifiers
    session_id: Optional[str] = None
    browser_context_id: Optional[str] = None
    page_id: Optional[str] = None
    dom_selector: Optional[str] = None

    # Native Desktop Identifiers
    process_id: Optional[int] = None
    process_name: Optional[str] = None
    window_handle: Optional[int] = None
    window_ref: Optional[str] = None
    uia_runtime_id: Optional[str] = None
    control_type: Optional[str] = None
    element_name: Optional[str] = None

    # Visual Identifiers
    visual_target_name: Optional[str] = None
    coordinates: Optional[Dict[str, Any]] = None
    bounds: Optional[Dict[str, Any]] = None

    # Lineage and Metadata
    authorization_scope: str = "computer_control"
    last_observed_at: Optional[datetime] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

---

## 3. Surface Classification Logic (`targets/classifier.py`)

The `SurfaceClassifier` inspects target properties and assigns a deterministic `SurfaceType`:

1. **`BROWSER_DOM`**:
   - Target specifies an active `session_id` and `dom_selector`, or `target_type` is `BROWSER_ELEMENT` / `BROWSER_PAGE`.
2. **`NATIVE_UIA`**:
   - Target has a valid `uia_runtime_id`, `control_type`, or `element_name` without custom-rendered flags.
3. **`NATIVE_WIN32`**:
   - Target has an explicit numeric `window_handle` and legacy control identifiers without UIA metadata.
4. **`CUSTOM_RENDERED`**:
   - Known DirectX, OpenGL, or Canvas processes (e.g. game engines, 3D renderers, or un-instrumented Electron canvases) flagged via window class name or process attributes.
5. **`EMBEDDED_WEBVIEW`**:
   - Native windows containing an active CEF, WebView2, or Electron viewport.
6. **`UNKNOWN`**:
   - Target lacks structural identifiers; falls back immediately to visual grounding.

---

## 4. Target Identity Validation & Recycled HWND Protection (`targets/identity.py`)

The `TargetIdentityValidator` performs pre-execution sanity checks:

```python
def validate_target(self, target: InteractionTarget) -> None:
    # 1. Coordinate Boundary Checks
    if target.coordinates:
        x, y = target.coordinates.get("x", 0), target.coordinates.get("y", 0)
        if x < 0 or y < 0:
            raise TargetResolutionError(f"Target coordinates out of bounds: ({x}, {y})")

    # 2. Recycled HWND Verification
    if target.window_handle and target.process_id:
        current_pid = self._get_pid_from_hwnd(target.window_handle)
        if current_pid != target.process_id:
            raise StaleTargetError(
                f"HWND {target.window_handle} was recycled: expected PID {target.process_id}, found PID {current_pid}"
            )

    # 3. DOM Selector Sanity
    if target.surface_type == SurfaceType.BROWSER_DOM and target.dom_selector:
        if not target.dom_selector.strip():
            raise TargetResolutionError("Empty DOM selector provided for browser target.")
```
