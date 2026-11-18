# Procedure Replay & Execution Engine

## 1. Overview & Objectives

The Procedure Execution Engine (`app/computer/workflow_reliability/replay/executor.py`) replays `ReusableProcedure` specifications against live applications with real-time target re-resolution, multi-method dispatch, precondition verification, and step-by-step progress tracking.

The engine is engineered for resilience against UI changes, network lag, and application timing variations.

---

## 2. Execution Modes

The engine supports three distinct replay execution modes:

| Mode | Execution Behavior | User Interaction | Safety / Checkpointing |
| :--- | :--- | :--- | :--- |
| `dry_run` | Simulates target resolution and validates parameters without firing physical clicks or keystrokes. | Fully automated, non-intrusive. | Read-only; generates synthetic trace for verification. |
| `step_by_step` | Executes a single step and pauses, awaiting explicit user confirmation or inspection before the next step. | Interactive stepping in frontend Replay Inspector. | Full checkpoint generated after every step; user can modify parameters mid-flight. |
| `automatic_authorized` | Executes continuously from start to finish within Stage 14 preauthorized policy grants. | Background execution with emergency pause available. | Automatic checkpoints created at step boundaries; halts immediately on assertion failure. |

---

## 3. Dynamic Target Re-Resolution

Live UIs frequently shift, re-render, or change DOM hierarchies between runs. To prevent fragile failures, the execution engine uses a 4-tier dynamic re-resolution hierarchy:

1. **Primary Structural Selector**: Checks the primary selector (e.g. CSS selector for browser, `AutomationId` for Windows UIA).
2. **Alternative Structural Selectors**: If primary fails, attempts alternate structural anchors (e.g. XPath, Name, ClassName).
3. **Fuzzy Text & OCR Matching**: If structural queries fail, queries the OCR engine for matching candidate text in the expected bounding neighborhood.
4. **Normalized Spatial Proximity**: Falls back to normalized coordinate bounds if surrounding visual anchors confirm viewport consistency.

If all resolution tiers fail within `step.timeout_ms`, the engine flags the step as failed, captures a diagnostic screenshot, records a failure checkpoint, and halts execution cleanly.

---

## 4. Assertion & Condition Verification

Each step executes in an explicit verification envelope:
```
Preconditions Check -> Method Dispatch -> Postconditions Check -> Checkpoint Creation
```

### Precondition Checks
Before dispatching an action, the executor evaluates all declared `preconditions`:
- `window_active`: Verifies target process and window title are in foreground.
- `url_matches`: Confirms current browser tab matches expected pattern.
- `element_exists`: Confirms target is present and interactive.

### Postcondition Checks
After dispatching an action, the executor verifies expected side-effects:
- `text_contains`: Asserts success badge or expected confirmation text appeared.
- `element_not_exists`: Asserts loading dialog or modal dismissed.
- `url_matches`: Confirms navigation to target destination completed.

---

## 5. Execution State Machine & Lifecycle

Execution sessions transition through deterministic states:
```
PENDING -> INITIALIZING -> RUNNING -> PAUSED (optional) -> COMPLETED / FAILED / ABORTED
```

The execution progress is exposed over REST API (`GET /api/v1/reliability/executions/{execution_id}`) and streamed to the desktop frontend via Server-Sent Events (SSE) for real-time visualization.
