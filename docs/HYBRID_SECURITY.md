# Stage 19: Hybrid Engine Security, Authorization & Session Guards

## 1. Fail-Closed Security Philosophy

The Hybrid Computer Interaction Engine operates directly on the user's operating system, web sessions, and native applications. It implements a strict **fail-closed security architecture**:

1. **Global Emergency Stop Integration:** Any active emergency stop (from Stage 14 killswitch or physical `Pause/Break` key) aborts execution immediately via `HybridExecutionGuard`.
2. **Session Interactivity Guard:** If the Windows workstation is locked (e.g. Win+L, screensaver lock, or RDP disconnect), execution is blocked via `SessionLockedError` to prevent blind input injection onto an invisible lockscreen.
3. **Stage 14 Centralized Policy Evaluation:** Actions are mapped to Stage 14 categories (`browser`, `desktop`, `system`) and evaluated against user-configured grants and authorization rules before any adapter is dispatched.
4. **No Privilege Escalation on Fallback:** A fallback adapter cannot be selected if the caller lacks authorization for that secondary method.

---

## 2. Windows Desktop Session Lock Detection

```python
def is_session_locked(self) -> bool:
    """Detect whether Windows workstation is currently locked."""
    try:
        # 0x0100 is DESKTOP_SWITCHDESKTOP permission
        hdesk = ctypes.windll.user32.OpenInputDesktop(0, False, 0x0100)
        if not hdesk:
            return True
        ctypes.windll.user32.CloseDesktop(hdesk)
        return False
    except Exception as exc:
        logger.debug("Workstation lock check error: %s", exc)
        return False
```

---

## 3. Authorization Bridge Mapping (`HybridAuthorizationBridge`)

The bridge maps hybrid operations to Stage 14 permissions:

| Hybrid Action | Selected Method | Stage 14 Category | Stage 14 Action Name | Default Risk |
|---|---|---|---|---|
| `click` | `BROWSER_DOM` | `browser` | `browser_click` | `LOW` |
| `click` | `WINDOWS_UIA` | `desktop` | `desktop_invoke` | `LOW` |
| `click` | `WINDOWS_WIN32` | `desktop` | `win32_click` | `MODERATE` |
| `click` | `VISUAL_GROUNDING`| `desktop` | `visual_click` | `MODERATE` |
| `enter_text` | `BROWSER_DOM` | `browser` | `browser_fill` | `LOW` |
| `enter_text` | `WINDOWS_UIA` | `desktop` | `desktop_set_value` | `LOW` |
| `enter_text` | `VISUAL_GROUNDING`| `desktop` | `visual_type` | `HIGH` |
| `submit` | Any | `browser`/`desktop` | `submit_application`| `HIGH` (Requires Approval) |
