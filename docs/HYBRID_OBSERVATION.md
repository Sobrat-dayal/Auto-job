# Stage 19: Cross-Method Observation & Unified Perception

## 1. Overview & Goal

Different automation adapters capture vastly different representations of the desktop:
- **Browser DOM:** HTML tags, CSS classes, computed accessibility roles, and interactive input elements.
- **Windows UIA:** Accessibility control tree, AutomationIds, ControlTypes, and Pattern availability.
- **Win32:** HWND hierarchy, class names, window titles, and style bitmasks.
- **Visual Grounding:** Display pixel snapshots, OCR bounding boxes, text lines, and UI element coordinate predictions.

The `ObservationCoordinator` (`observations/coordinator.py`) unifies these representations into a normalized `InteractionObservation` model.

---

## 2. InteractionObservation Contract

```python
class InteractionObservation(BaseModel):
    observation_id: str = Field(default_factory=lambda: f"obs_{uuid.uuid4().hex[:12]}")
    target_id: str
    method: InteractionMethod
    surface_type: SurfaceType

    # Normalized text and structural summary
    observed_text: Optional[str] = None
    structure_summary: Optional[str] = None

    # Detailed cross-modality structures
    dom_elements: List[Dict[str, Any]] = Field(default_factory=list)
    uia_elements: List[Dict[str, Any]] = Field(default_factory=list)
    visual_detections: List[Dict[str, Any]] = Field(default_factory=list)

    # Health and freshness
    is_valid: bool = True
    is_stale: bool = False
    captured_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: Dict[str, Any] = Field(default_factory=dict)
```

---

## 3. Observation Strategy

1. **Lightweight Structural Capture First:**
   - If the target is classified as `BROWSER_DOM` or `NATIVE_UIA`, the coordinator requests structural tree data from the primary adapter.
   - Text is extracted from DOM inner text or UIA Name/Value properties in < 15ms.

2. **Visual Perception on Demand:**
   - Visual capture (MSS/GDI screenshot) is only triggered when `include_visual=True`, when the target is `CUSTOM_RENDERED` / `UNKNOWN`, or when the structural observation is empty/stale.
   - Saves substantial CPU, GPU memory, and battery consumption compared to continuous screenshot loops.

3. **Stale Target Invalidation:**
   - Observations older than 2.0 seconds are flagged as `is_stale=True`.
   - Before executing physical coordinate clicks, coordinates are re-verified against the fresh observation.
