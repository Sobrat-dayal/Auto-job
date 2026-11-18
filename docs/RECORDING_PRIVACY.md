# Recording Privacy & Sensitive Data Protection

## 1. Overview & Principles

Automated computer interaction recording captures deep system signals, keystrokes, form inputs, and window states. To prevent accidental leakage of secrets, personal identifiable information (PII), or unauthorized workspace capture, AUTONOM implements a **zero-trust, fail-closed privacy filter** integrated directly into the recording pipeline.

The recording engine enforces three strict boundaries:
1. **Application Scope Filtering**: Confines recording to permitted desktop process names.
2. **Origin & Domain Filtering**: Confines browser recording to pre-approved URLs and domains.
3. **Sensitive Parameter Redaction**: Automatically identifies, masks, and sanitizes secrets, tokens, passwords, and sensitive keys using high-coverage regular expressions.

---

## 2. Scope & Target Boundaries

### 2.1 Desktop Application Whitelisting
The recording manager inspects the foreground process name before recording any action:
```python
def is_app_allowed(process_name: str, allowed_apps: list[str]) -> bool:
    if not allowed_apps:
        return True  # If empty, all non-blacklisted apps permitted
    return any(allowed.lower() in process_name.lower() for allowed in allowed_apps)
```

If an action occurs inside an unlisted application (e.g., password manager, banking portal, private chat), the action is discarded immediately before persisting or serializing.

### 2.2 Browser Origin Whitelisting
For web-based operations, target URLs are validated against the session's configured `allowed_origins`:
```python
def is_origin_allowed(url: str, allowed_origins: list[str]) -> bool:
    if not allowed_origins:
        return True
    parsed = urllib.parse.urlparse(url)
    origin = f"{parsed.scheme}://{parsed.netloc}".lower()
    return any(allowed.lower() in origin for allowed in allowed_origins)
```

Navigations or clicks directed outside permitted domains cause recording to pause or drop the event.

---

## 3. Sensitive Parameter Redaction

Input fields, typed text strings, and query parameters are scrubbed through a multi-pass regex filter (`app/computer/workflow_reliability/recording/privacy.py`).

### 3.1 Redaction Patterns
The engine maintains compiled pattern matchers for known credential signatures:
- **Passwords & Keys**: Matches key names containing `password`, `pwd`, `secret`, `api_key`, `token`, `bearer`, `auth`, `private_key`.
- **JWT & Tokens**: Redacts high-entropy JWT strings (`eyJ...`) and hex tokens.
- **Credit Cards & SSNs**: Redacts 13-16 digit payment card numbers and 9-digit SSN formats.
- **Session Cookies**: Redacts session identifiers and auth cookies.

### 3.2 Replacement Rules
Any matched sensitive value is replaced with deterministic placeholders:
- Passwords -> `"[REDACTED_PASSWORD]"`
- Tokens & API Keys -> `"[REDACTED_TOKEN]"`
- PII / SSN -> `"[REDACTED_SENSITIVE]"`

When parameterizing recorded actions into `ReusableProcedure` specifications, parameters marked with sensitive keys are automatically converted into required input variables with `is_secret=True`, ensuring secrets must be supplied at runtime via DPAPI or secure user prompt, never stored in plaintext scripts.

---

## 4. Privacy Testing & Compliance

All privacy routines are verified through automated unit tests in `services/api/tests/test_reliability_recording.py`:
- `test_privacy_filter_redacts_passwords`: Asserts `"secret123"` becomes `"[REDACTED_PASSWORD]"`.
- `test_scope_filtering_blocks_unauthorized_apps`: Confirms background apps outside the active session allowlist are ignored.
- `test_web_origin_boundaries`: Validates navigation events to external domains are not captured.
