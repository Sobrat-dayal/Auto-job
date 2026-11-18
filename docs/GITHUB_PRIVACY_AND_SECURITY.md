# Stage 22: GitHub Privacy, Secret Redaction & Security Perimeter

## 1. Zero-Exposure Security Model

AUTONOM's integration with GitHub enforces five fundamental security boundaries:

```
[External Repositories]
          │
          v
[SourceFilter (< 500 KB, no bin, safe paths)]
          │
          v
[SecretRedactor (Regex Pattern Scrubbing)]
   ├── Private Keys: RSA, OpenSSH, PGP
   ├── Cloud Tokens: AWS, GCP, Azure
   ├── API Keys: GitHub PAT, Slack, OpenAI
   └── Database URLs: postgres://, mysql://
          │
          v (Sanitized Excerpt)
[Internal Memory & UI Display]
```

---

## 2. Multi-Pattern Secret Redaction (`SecretRedactor`)

Developers occasionally commit private credentials to git repositories accidentally. Before any file content or commit diff is stored in the local SQLite database or displayed in the desktop UI, `SecretRedactor` scans the raw string against high-entropy regular expressions:

| Target Credential Pattern | Redaction Replacement |
| :--- | :--- |
| **RSA / OpenSSH / PGP Private Keys** (`-----BEGIN [A-Z ]*PRIVATE KEY-----...`) | `[REDACTED_SECRET]` |
| **GitHub Classic PAT** (`ghp_[A-Za-z0-9_]{36}`) | `[REDACTED_SECRET]` |
| **GitHub Fine-Grained PAT** (`github_pat_[A-Za-z0-9_]{82}`) | `[REDACTED_SECRET]` |
| **AWS Access Key ID** (`AKIA[0-9A-Z]{16}`) | `[REDACTED_SECRET]` |
| **AWS Secret Access Key** (`aws_secret_access_key = ...`) | `[REDACTED_SECRET]` |
| **JSON Web Tokens** (`ey[A-Za-z0-9_-]{10,}\.ey...`) | `[REDACTED_SECRET]` |
| **Database Connection Strings** (`(postgres\|mysql\|mongodb)://user:pass@host:port/db`) | `[REDACTED_SECRET]` |
| **Slack Webhooks / Tokens** (`xox[baprs]-[0-9]{10,}-...`) | `[REDACTED_SECRET]` |

If any secret match is found, `SecretRedactor.redact()` replaces the sensitive segment, increments the redaction counter in telemetry, and flags `has_redacted_secrets = True` on the resulting snippet.

---

## 3. Strict Sandboxing & Non-Execution Guarantees

1. **No Code Execution**: AUTONOM treats repository content strictly as plain text or JSON/TOML ASTs. It never invokes `python setup.py`, `npm install`, `cargo build`, or any script execution on downloaded source code.
2. **Path Traversal Defenses**: All file paths supplied from GitHub Trees or user inputs are validated against directory traversal patterns (`../`, `..\`, null bytes, Windows volume drives `C:`).
3. **DPAPI Vault Protection**: GitHub Personal Access Tokens are protected by Windows DPAPI machine/user encryption keys and AES-256-GCM. Decryption keys never leave the operating system's Cryptography API boundaries.
