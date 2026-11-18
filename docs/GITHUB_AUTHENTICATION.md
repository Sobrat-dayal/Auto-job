# Stage 22: GitHub Authentication & Credential Security

## 1. Authentication Modes

AUTONOM supports three distinct connection tiers to ensure privacy, flexibility, and compliance with corporate or personal security policies:

| Mode | Capabilities | Rate Limit | Token Required | Scope Level |
| :--- | :--- | :--- | :--- | :--- |
| **`PUBLIC_ONLY`** | Discovers public repositories, user profile metadata, public commit activity. | 60 requests/hr (per IP) | None | Zero scopes |
| **`PAT`** (Personal Access Token) | Access to private repositories, organizations, detailed PR reviews, commit stats. | 5,000 requests/hr | Fine-grained or Classic PAT | Read-only (`repo:read`, `read:user`) |
| **`MANUAL_URL`** | Inspects a single standalone public repository without full profile link. | 60 requests/hr (or shared PAT) | Optional | Zero or Read-only |

---

## 2. Personal Access Token (PAT) Security Architecture

### 2.1 Encryption at Rest (Windows DPAPI + AES-256-GCM)
Raw GitHub access tokens (`ghp_*`, `github_pat_*`) are never stored in plaintext within SQLite or JSON config files. Instead, AUTONOM utilizes the Stage 04 `CredentialManager`:
1. When a user enters a token in the Desktop UI, it is transmitted over localhost TLS/HTTP to `/api/v1/github/connections`.
2. The `GitHubConnectionManager` encrypts the token using the Windows Data Protection API (`CryptProtectData`), binding decryption strictly to the current Windows user session and hardware TPM.
3. The encrypted payload is wrapped in AES-256-GCM with associated authentication data (`provider="github"`).
4. A unique UUID reference key (`token_reference_id`) is stored in the database.
5. In all API responses and desktop UI views, the token is masked as `ghp_••••••••••••` or `github_pat_••••••••`.

```python
# Conceptual flow in GitHubConnectionManager
ref_id = await credential_manager.encrypt_secret(
    secret=token.strip(),
    provider="github",
    context=f"applicant_profile_{profile_id}"
)
conn.token_reference_id = ref_id
```

### 2.2 Scope Minimization & Permission Auditing
AUTONOM strictly adheres to the principle of least privilege. During connection setup and via `/api/v1/github/connections/{id}/permissions`, the system inspects the `X-OAuth-Scopes` header returned by GitHub.

- **Permitted Scopes**: `read:user`, `user:email`, `repo:status`, `public_repo`, `repo` (read-only usage).
- **Prohibited Write Scopes**: If write or administrative scopes are detected (`write:repo_hook`, `admin:repo_hook`, `delete_repo`), AUTONOM surfaces a security warning in the UI advising the user to regenerate a fine-grained token with read-only permissions.
- **Enforced Read-Only Operations**: Regardless of the token's granted scopes, AUTONOM's internal HTTP client only implements `GET` and `HEAD` methods against GitHub APIs. No `POST`, `PUT`, `PATCH`, or `DELETE` requests to repository endpoints exist in the codebase.

---

## 3. Token Rotation and Revocation

1. **Explicit Disconnection**: When the user clicks **Disconnect** in the desktop client, `/api/v1/github/connections/{id}/disconnect` is triggered:
   - The encrypted secret is permanently wiped from the Windows DPAPI vault via `credential_manager.delete_secret()`.
   - The connection status is set to `REVOKED`.
   - Cached repository metadata, trees, and unconfirmed candidate items are purged.
2. **Expired or Revoked Token Handling**: If GitHub returns HTTP 401 Unauthorized or 403 Forbidden with `Bad credentials`, AUTONOM immediately updates the connection status to `EXPIRED`, suspends all background sync jobs, and alerts the applicant in the desktop Command Center.
