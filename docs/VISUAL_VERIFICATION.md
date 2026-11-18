# Visual Action Verification & State Transitions (Stage 18)

## 1. Before/After Verification Paradigm

Visual automation must never operate "blindly" or assume that an input dispatch succeeded. `VisualActionVerifier` (`app/visual/execution/verification.py`) mandates post-action state verification:

```
[Pre-Action Observation] ──► Capture Frame (T0)
           │
           ▼
[Execute Action Dispatch] ──► SendInput (Click / Keystroke)
           │
           ▼ (Stabilization Delay: 200–500 ms)
[Post-Action Observation] ──► Capture Frame (T1)
           │
           ▼
[State Difference Calculation]
   ├─ Pixel Diff Calculation (ImageChops delta)
   ├─ Bounding Box Region Delta
   └─ Post-Action OCR Assertion (Expected Text Present / Gone)
           │
           ▼
[Verification Outcome]
   ├─ VERIFIED_SUCCESS: Visible state transition observed (>1.0% diff or expected text)
   ├─ VERIFIED_FAILURE: No visible change or unexpected error dialog appeared
   └─ UNCERTAIN: Subtle change below noise threshold; flagged for review
```

---

## 2. Verification Criteria

### 1. Pixel Difference Metric
- Compares T0 and T1 frames after aligning dimensions.
- Ignores subpixel antialiasing and cursor blink noise (<15 luminosity delta).
- A valid UI interaction typically yields 0.5%–15% pixel difference (e.g. dropdown opening, button highlighting, tab changing).

### 2. OCR Text Assertions
- When an action specifies `expected_text` (e.g. typing text into an input or opening a dialog titled "Confirm"):
  - Post-action OCR scans the focused area.
  - Confirms target string appeared (or disappeared in the case of closing a modal).

---

## 3. Visual State Machine (`VisualStateMachine`)

Every visual computer task transitions through a deterministic state machine:
- `PENDING`: Task queued.
- `OBSERVING`: Capturing initial screen state.
- `GROUNDING`: Locating target UI elements.
- `ACTING`: Dispatching mouse/keyboard input.
- `VERIFYING`: Evaluating post-action visual state change.
- `RECOVERING`: Attempting bounded recovery upon verification failure.
- `COMPLETED` / `FAILED` / `CANCELLED`: Terminal states.
