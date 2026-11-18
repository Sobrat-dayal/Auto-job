# Action Recording Architecture

## 1. Overview & Objectives

The Action Recording Engine in AUTONOM Stage 20 provides deterministic, low-overhead, multi-modal capture of user and agent interactions across all supported computer interaction surfaces:
- **Browser DOM** (Playwright execution hooks, navigation events, form filling, element clicks)
- **Windows UI Automation (UIA)** (COM patterns, accessible control clicks, value changes)
- **Native Win32** (Window messaging, menu item selections, standard controls)
- **Visual Grounding & Coordinates** (Screen region clicks, normalized bounding boxes, OCR text targets)

The engine captures raw interactions, enriches them with contextual metadata, scrubs sensitive data through a strict privacy filter, and structures them into an immutable, chronologically ordered sequence of `RecordedAction` records stored in persistent SQLite storage.

---

## 2. Component Architecture

```
+----------------------------------------------------------------------------------------------------+
|                                INTERACTION EVENT PRODUCERS                                         |
|  [Playwright DOM]      [Windows UIA COM]      [Win32 Messages]      [Visual Grounding / SendInput] |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                           ACTION CAPTURE SUBSCRIBER & NORMALIZER                                   |
| - Timestamping & Ordering (Monotonic + UTC)                                                        |
| - Target Disambiguation & Fallback Selectors (DOM, AutomationId, OCR text, normalized coordinates)  |
| - Pre-State Snapshot Fingerprinting                                                                |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                               PRIVACY & SCOPE FILTERING GATEWAY                                    |
| - Process & Window Title Scope Check                                                               |
| - URL & Web Origin Filter                                                                          |
| - Sensitive Parameter Regex Redaction ([REDACTED_PASSWORD], [REDACTED_TOKEN])                      |
+--------------------------------------------------+-------------------------------------------------+
                                                   |
                                                   v
+----------------------------------------------------------------------------------------------------+
|                            RECORDING SESSION MANAGER & PERSISTENCE                                 |
| - Session State Machine: CREATED -> ACTIVE -> PAUSED -> COMPLETED                                  |
| - SQLite `recording_sessions` & `recorded_actions` Tables                                          |
| - Cryptographic Checkpoint Anchor Creation                                                         |
+----------------------------------------------------------------------------------------------------+
```

---

## 3. Data Contracts & Data Structures

Every recorded interaction is normalized into a `RecordedAction` entity defined in `app/computer/workflow_reliability/contracts.py`:

```python
class RecordedAction(BaseModel):
    action_id: str = Field(default_factory=lambda: f"act_{uuid4().hex[:12]}")
    session_id: str
    sequence_index: int
    adapter: InteractionMethod  # BROWSER_DOM, NATIVE_UIA, NATIVE_WIN32, VISUAL
    action_type: str            # click, type, navigate, select, hotkey, scroll
    target: InteractionTarget
    parameters: dict[str, Any] = Field(default_factory=dict)
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    duration_ms: float = 0.0
    pre_state_fingerprint: str | None = None
    post_state_fingerprint: str | None = None
    success: bool = True
    error_message: str | None = None
    metadata: dict[str, Any] = Field(default_factory=dict)
```

Key features of the contract:
1. **Multi-Target Resolution**: The `InteractionTarget` carries selectors across multiple modalities (e.g., CSS selector, UIA AutomationId, bounding coordinates, and OCR text), enabling resilient re-resolution during replay.
2. **Deterministic Sequencing**: `sequence_index` establishes strict monotonic execution order.
3. **Fingerprint Anchors**: `pre_state_fingerprint` records the active window title, process name, and URL prior to execution, ensuring preconditions can be verified during replay.

---

## 4. Multi-Modal Event Capture & Normalization

### 4.1 Browser DOM Normalization
When the browser adapter completes an action:
- `action_type`: `"navigate"`, `"click"`, `"fill"`, `"select"`.
- `target`: CSS selector, XPath, text content, and enclosing form attributes.
- `parameters`: Form input value (if not classified as secret), target URL, or keyboard sequence.

### 4.2 Windows UIA Normalization
When structural desktop actions execute:
- `action_type`: `"click"`, `"set_value"`, `"invoke"`.
- `target`: `automation_id`, `control_type`, `class_name`, `window_title`, and hierarchical bounding box.
- `parameters`: Value string, hotkey combo, or pattern identifier.

### 4.3 Visual & Coordinate Normalization
When visual actions execute:
- `action_type`: `"click"`, `"type"`, `"mouse_drag"`.
- `target`: Normalized screen coordinates `(0.0..1.0)` independent of physical display resolution, combined with OCR candidate text and surrounding landmark descriptions.

---

## 5. Storage & Persistence

Recorded sessions are persisted in the local SQLite database via two tables:
- `recording_sessions`: Stores session metadata, application scope, status (`active`, `paused`, `completed`, `cancelled`), and action count.
- `recorded_actions`: Stores full JSON-serialized action payloads indexed by `session_id` and `sequence_index`.

Write operations leverage SQLite Write-Ahead Logging (WAL) for sub-millisecond persistence without blocking UI threads.
