# AUTONOM — Secure Storage, Windows DPAPI & Cryptographic Protection

## 1. Threat Model & Security Objectives

AUTONOM operates on user endpoints and automates sensitive career tasks, requiring the storage of:

- **Personal Identifiable Information (PII)**: Applicant phone numbers, home addresses, personal email addresses, salary requirements.
- **Service Integration Secrets**: API keys (Anthropic Claude, OpenAI, Google Gemini), OAuth refresh tokens, session cookies for job portals (LinkedIn, Indeed).
- **Authentication Credentials**: Portal logins and automation tokens.

### Security Guarantees

1. **Zero Plaintext Secrets at Rest**: Sensitive data is never written in plaintext to SQLite tables, WAL logs, JSON configuration files, application traces, or log outputs.
2. **User-Bound Master Key**: The cryptographic master key is encrypted directly using the **Windows Data Protection API (DPAPI)**, binding decryption strictly to the current logged-in Windows user account on that specific workstation.
3. **Hardware / Machine Decoupling**: If an attacker copies the `.db` file or `.vault.key` to another machine or another Windows user profile, decryption fails cryptographically.
4. **Authenticated Ciphertext**: All field-level and secret encryption uses **AES-256-GCM**, providing both confidentiality and cryptographic integrity verification (detecting any tampering with ciphertext).

---

## 2. Cryptographic Architecture

The security subsystem is implemented across three modules in `services/api/app/security/`:

```
services/api/app/security/
├── dpapi.py       # Win32 CryptProtectData / CryptUnprotectData via ctypes
├── vault.py       # AES-256-GCM envelope encryption and master key lifecycle
└── credentials.py # SecureCredentialManager for provider secrets
```

### Key Hierarchy & Envelope Encryption

```
+-------------------------------------------------------------------+
|                     Current Windows User Logon                    |
|             (Windows LSA / Credential Guard / DPAPI)              |
+-------------------------------------------------------------------+
                                  |
                   CryptProtectData / CryptUnprotectData
                                  v
+-------------------------------------------------------------------+
|               DPAPI-Protected Master Vault Key File               |
|            Path: %LOCALAPPDATA%\AUTONOM\config\.vault.key         |
|              (32-byte Cryptographically Secure Secret)            |
+-------------------------------------------------------------------+
                                  |
                     AES-256-GCM Authenticated Encryption
                                  v
+-------------------------------------------------------------------+
|                     Encrypted Persistent Storage                  |
|  - Table applicant_profiles -> contact_info_encrypted (JSON)      |
|  - Table credential_references -> encrypted_payload (Tokens)      |
+-------------------------------------------------------------------+
```

---

## 3. Implementation Details

### Native Windows DPAPI (`app/security/dpapi.py`)

Utilizes Python's `ctypes` to interface directly with `crypt32.dll`:

- **`CryptProtectData`**: Encrypts plaintext bytes using Windows machine/user credentials.
- **`CryptUnprotectData`**: Decrypts ciphertext bytes only when executed under the identical Windows user context.

```python
# Ctypes DATA_BLOB struct mapping
class DATA_BLOB(ctypes.Structure):
    _fields_ = [("cbData", ctypes.wintypes.DWORD), ("pbData", ctypes.POINTER(ctypes.c_byte))]
```

### AES-256-GCM Vault (`app/security/vault.py`)

- **Key Generation**: 32 bytes from `os.urandom(32)`.
- **Key Storage**: Encrypted with DPAPI and saved to `%LOCALAPPDATA%\AUTONOM\config\.vault.key` with restricted permissions.
- **Payload Encryption**: Generates a unique 96-bit (12-byte) random initialization vector (`nonce`) for every encryption operation. Output format:
  ```
  [12 bytes: IV/Nonce] + [Ciphertext] + [16 bytes: GCM Authentication Tag]
  ```
- **Base64 Encoding**: Output is encoded into URL-safe Base64 for clean storage in database text/blob columns.

---

## 4. Field-Level Contact Info Encryption

In `app/repositories/profiles.py`, applicant contact information (email, phone number, address) is separated from general public profile details (full name, summary, headline):

```python
# When saving:
contact_json = json.dumps(contact_info)
encrypted_blob = vault.encrypt_string(contact_json, associated_data=profile_id)
# Only encrypted_blob is stored in SQLite column `contact_info_encrypted`.

# When retrieving:
decrypted_json = vault.decrypt_string(encrypted_blob, associated_data=profile_id)
contact_info = json.loads(decrypted_json)
```

The `profile_id` is passed as AES-GCM Associated Data (`aad`), guaranteeing that ciphertext cannot be swapped between different profile rows.

---

## 5. Credential Masking & API Protection

The `GET /api/v1/integrations/credentials/status` endpoint provides the frontend with operational knowledge of configured providers without leaking secrets:

```json
[
  {
    "provider": "anthropic_claude",
    "credential_type": "api_key",
    "status": "active",
    "is_configured": true,
    "created_at": "2026-11-16T15:00:00Z"
  }
]
```

- Plaintext secrets are strictly write-only via `POST /api/v1/integrations/credentials`.
- Deletion is supported via `DELETE /api/v1/integrations/credentials/{provider}`.
- Secret values never enter client-side state, browser memory, or SSE broadcast logs.
