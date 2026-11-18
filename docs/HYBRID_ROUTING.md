# Stage 19: Dynamic Control Routing Engine

## 1. Overview & Policy Hierarchy

The AUTONOM Hybrid Routing Engine (`routing/router.py`) selects the optimal interaction adapter based on deterministic surface preferences, adapter availability, capability match, latency, and resource cost.

### 1.1. Deterministic Preference Orders

```python
SURFACE_METHOD_PREFERENCES: Dict[SurfaceType, List[InteractionMethod]] = {
    SurfaceType.BROWSER_DOM: [
        InteractionMethod.BROWSER_DOM,
        InteractionMethod.VISUAL_GROUNDING,
    ],
    SurfaceType.NATIVE_UIA: [
        InteractionMethod.WINDOWS_UIA,
        InteractionMethod.WINDOWS_WIN32,
        InteractionMethod.VISUAL_GROUNDING,
    ],
    SurfaceType.NATIVE_WIN32: [
        InteractionMethod.WINDOWS_WIN32,
        InteractionMethod.WINDOWS_UIA,
        InteractionMethod.VISUAL_GROUNDING,
    ],
    SurfaceType.CUSTOM_RENDERED: [
        InteractionMethod.VISUAL_GROUNDING,
        InteractionMethod.WINDOWS_WIN32,
    ],
    SurfaceType.EMBEDDED_WEBVIEW: [
        InteractionMethod.BROWSER_DOM,
        InteractionMethod.WINDOWS_UIA,
        InteractionMethod.VISUAL_GROUNDING,
    ],
    SurfaceType.UNKNOWN: [
        InteractionMethod.VISUAL_GROUNDING,
    ],
}
```

---

## 2. Transparent Scoring Model (`routing/scoring.py`)

Candidate adapters are scored on a scale from 0.0 to 100.0:

$$\text{FinalScore} = \text{CapabilityFit} \times 0.40 + \text{ReliabilityScore} \times 0.25 + \text{CostScore} \times 0.15 + \text{PreferenceBonus} \times 0.20$$

1. **Capability Fit (0..100):** Based on adapter confidence and whether the requested action (e.g. `submit`, `enter_text`) is supported.
2. **Reliability Score (0..100):** Calculated from runtime historical telemetry:
   $$\text{Reliability} = \frac{\text{Successes}}{\text{Successes} + \text{Failures}} \times 100$$
   (defaults to 85.0 if no attempts have been recorded).
3. **Cost Score (0..100):**
   - Structural adapters (`BROWSER_DOM`, `WINDOWS_UIA`, `WINDOWS_WIN32`) have low compute overhead (score 90..95).
   - Visual grounding incurs high GPU/CPU capture and OCR latency (score 50..60).
4. **Preference Bonus (0..100):**
   - Rank 0 in surface preference receives +25 bonus points.
   - Rank 1 receives +10 bonus points.
   - Rank 2+ receives 0 bonus points.

---

## 3. Explainable Routing Decision Record

Every routing evaluation generates an immutable `RoutingDecisionRecordSchema` persisted to the database (`RoutingDecisionRecord`):
- `decision_id`: Unique traceable ID (`dec_...`).
- `selected_method`: The winning adapter.
- `candidate_methods`: List of all probed adapters considered.
- `rejected_methods`: Dictionary mapping rejected adapters to their machine-readable rejection rationale.
- `scoring`: Exact numeric breakdown per candidate.
- `rationale`: Human-readable summary explaining why the method was selected.
