# Windows Visual Input Dispatch & Lease Management (Stage 18)

## 1. Win32 `SendInput` Dispatch Adapter

`SendInputAdapter` (`app/visual/input/adapter.py`) interfaces directly with the native Windows `user32.dll` `SendInput` API, providing clean mouse and keyboard simulation:

### Mouse Actions
- **Move Pointer**: Normalizes target coordinates to 0..65535 space and dispatches `MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE | MOUSEEVENTF_VIRTUALDESK`.
- **Clicks & Double Clicks**: Dispatches paired `MOUSEEVENTF_LEFTDOWN` and `MOUSEEVENTF_LEFTUP` events separated by natural human-like jitter delays (30–80 ms).
- **Right Clicks & Context Menus**: Dispatches `MOUSEEVENTF_RIGHTDOWN` / `MOUSEEVENTF_RIGHTUP`.
- **Drag & Drop**: Holds mouse down at origin point, moves across interpolated trajectory steps, and releases at target point.
- **Scroll**: Dispatches `MOUSEEVENTF_WHEEL` with signed delta multiples (120 units per scroll notch).

### Keyboard Actions
- **Keystrokes**: Translates standard key tokens ("Enter", "Tab", "Escape", "Backspace") to Windows Virtual Key (VK) codes and dispatches `KEYEVENTF_KEYDOWN` / `KEYEVENTF_KEYUP`.
- **Unicode Text Typing**: Uses `KEYEVENTF_UNICODE` for full UTF-16 character support without requiring clipboard modification.

---

## 2. Input Ownership & Concurrency Leases: `InputOwnershipManager`

To prevent race conditions where multiple background agents or background tasks attempt simultaneous mouse or keyboard actions:
1. An agent or task must acquire an **exclusive input lease** (`acquire_lease(owner_id, duration_seconds)`).
2. The manager issues a unique cryptographically random token (`lease_{owner}_{uuid}`).
3. Conflicting requests from other agents without the active token are rejected.
4. Leases expire automatically after their bounded duration (default 5–10s) to prevent permanent system lockup if an agent crashes.
5. Explicit `release_lease(token)` frees the input pipeline immediately upon task completion.

---

## 3. Human Inactivity & Intervention Detection

When a human user moves the physical mouse or types while AUTONOM is operating:
- The system detects cursor position deviation.
- Action dispatch pauses gracefully to yield priority to human input.
- Resumes only after configurable human idle period (default 2.0s).
