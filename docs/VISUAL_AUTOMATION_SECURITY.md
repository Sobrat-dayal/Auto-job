# Visual Automation Security & Fail-Closed Guardrails (Stage 18)

## 1. Fail-Closed Emergency Stop (Killswitch)

`VisualSecurityGuard` (`app/visual/security/guard.py`) guarantees immediate termination of all visual capture, grounding, and input operations whenever safety boundaries are breached:

1. **Hardware Killswitch (`Pause / Break` Key)**:
   - Dedicated global keyboard hook listening for the standard Windows `Pause / Break` key.
   - Operates independently of the browser or React frontend.
   - Instantly sets `emergency_stop_active = True`.
2. **REST API Emergency Stop**:
   - `POST /api/v1/visual/killswitch/trigger`: Allows any frontend component or external monitor to trigger emergency stop immediately.
   - `POST /api/v1/visual/killswitch/reset`: Requires explicit manual user re-authorization to restore operational state.
3. **Session Lock Detection**:
   - Inspects `user32.GetForegroundWindow()` and workstation session status.
   - If workstation is locked (`Win + L`) or switches to secure desktop, all automation halts immediately.

---

## 2. Privacy & Credential Masking (`VisualPrivacyFilter`)

Screenshots may capture confidential user information. `VisualPrivacyFilter` (`app/visual/security/privacy.py`) enforces strict data sanitization:
- **Sensitive Window Allowlist / Denylist**: Windows belonging to password managers (Bitwarden, 1Password, KeePass), banking domains, or Windows credential prompts are forbidden from visual capture.
- **Visual OCR Redaction**: Text containing regex patterns for credit cards, API keys (`sk-...`, Bearer tokens), social security numbers, or password fields are masked with solid black rectangles before being passed to LLMs or stored in database logs.

---

## 3. Integration with Stage 14 Granular Authorization

All visual actions require policy authorization:
- `visual_capture_display` / `visual_capture_window`: Checked against `pol_system_read_baseline`.
- `visual_run_ocr` / `visual_ground`: Read-only perception permissions.
- `visual_execute_action` / `visual_click` / `visual_enter_text`: High-privilege actions requiring active capability grant and policy evaluation. Actions outside approved application boundaries trigger an escalation request in the Approvals Workspace.
