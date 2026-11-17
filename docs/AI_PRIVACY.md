# AUTONOM — AI Privacy & Security Architecture (Stage 11)

## 1. Zero-Cloud Local Privacy Boundary

AUTONOM is designed with a **local-first privacy architecture**:

1. **Local Loopback Isolation**: Local inference executes entirely within the user's workstation over loopback address `127.0.0.1:11434`. No telemetry, analytics, or prompt data is transmitted across the internet.
2. **Strict Privacy Enforcement (`is_local_only=True`)**:
   - When a task involves Personally Identifiable Information (PII), sensitive user profile fields, financial records, or credentials, the request is flagged with `is_local_only=True`.
   - The Intelligent Model Router strictly rejects any cloud candidate, regardless of prompt length or task complexity.
   - If no local model is available, the request fails safely with `ProviderUnavailableError` rather than leaking data to a cloud endpoint.
3. **No Automatic Model Downloads**: AUTONOM will never autonomously trigger large multi-gigabyte weight downloads (`ollama pull`) or chargeable cloud API calls without explicit user authorization.

---

## 2. Windows DPAPI Keystore Integration

Cloud API credentials (such as OpenAI and Anthropic API keys) are never stored in plaintext JSON files or code repositories:
- Keys are encrypted using native **Windows Data Protection API (DPAPI)** via `CryptProtectData`.
- Stored exclusively in the protected SQLite database via `DPAPIVault`.
- Decrypted into process memory only at the instant of outbound HTTPS API invocation.
- Secret values are automatically redacted in application logs (`services/api/app/security/redaction.py`).
