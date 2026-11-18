# Desktop Action Contracts & Execution Engine Specification (Stage 17)

## 1. Overview

AUTONOM's action engine dispatches strongly-typed desktop operations against validated Windows controls and windows.

Every action execution follows a strict lifecycle:
1. **Security & Lock Gate Check**: Verification that Emergency Stop is off and Windows is interactive.
2. **Window Vitality Check**: Validation that `window_ref` HWND exists and PID matches.
3. **Application Authorization Check**: Verification that the target application executable is in the approved allowlist.
4. **Target Element Resolution**: Resolves target control via `element_ref` or semantic `ElementQuery` locator.
5. **Pattern Invocation with Fallback**: Executes native UIA pattern or falls back to Win32 messaging.
6. **Post-Action Mutation Verification**: Asserts that target state actually changed.
7. **Audit & Event Emission**: Records action to database and streams event via EventBus.

---

## 2. Action Request Contract: `DesktopActionRequest`

```python
class DesktopActionRequest(BaseModel):
    action_type: DesktopActionType
    window_ref: str
    element_ref: str | None = None
    locator: ElementQuery | None = None
    value: str | None = None
    key: str | None = None
    modifiers: list[str] = Field(default_factory=list)
    timeout_ms: int = Field(default=15000, ge=1000, le=60000)
    verify: bool = True
    expected_outcome: str | None = None
```

### Supported Action Types (`DesktopActionType`)

- `invoke`: Triggers buttons, links, menu items (`IUIAutomationInvokePattern`).
- `set_value`: Sets text in text fields or editable comboboxes (`IUIAutomationValuePattern`).
- `toggle`: Flips checkboxes and switches (`IUIAutomationTogglePattern`).
- `select`: Selects items in lists, comboboxes, or tab bars (`IUIAutomationSelectionItemPattern`).
- `expand` / `collapse`: Expands or collapses hierarchical trees and dropdowns (`IUIAutomationExpandCollapsePattern`).
- `scroll`: Scrolls container viewports (`IUIAutomationScrollPattern`).
- `read_text`: Reads current text content from controls.
- `activate_window`: Brings window to foreground and restores if minimized.
- `close_window`: Gracefully posts `WM_CLOSE` to window message queue.
- `press_key`: Dispatches keystroke or text string to verified foreground window.

---

## 3. Post-Action Mutation Verification (`StructuralActionVerifier`)

A major source of automation fragility is fire-and-forget execution where an action reports success even if the target application silently ignored the event.

`StructuralActionVerifier` (`app/computer/actions/verifier.py`) performs active post-action verification:

| Action Type | Verification Assertions |
| :--- | :--- |
| `set_value` | Re-reads `CurrentValue` from `ValuePattern` to verify text matches desired string. |
| `toggle` | Queries `CurrentToggleState` to assert state transitioned (e.g., 0 to 1). |
| `select` | Checks `IsSelected` on `SelectionItemPattern`. |
| `expand` / `collapse` | Queries `ExpandCollapseState` (Expanded: 1, Collapsed: 0). |
| `activate_window` | Asserts `user32.GetForegroundWindow() == target_hwnd`. |
| `close_window` | Asserts `not user32.IsWindow(target_hwnd)` after grace timeout. |

Verification results are returned in `DesktopActionResult`:
- `status`: `"succeeded"`, `"failed"`, or `"blocked"`
- `verification_status`: `"verified"`, `"unverified"`, or `"failed"`
- `duration_ms`: Execution time in milliseconds.
