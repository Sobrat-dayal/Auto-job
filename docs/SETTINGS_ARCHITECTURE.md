# AUTONOM — Settings Architecture Specification

## 1. Overview & Architectural Role

The Settings & Operational Controls workspace represents the primary administrative and configuration hub for AUTONOM. As the culmination of **Phase 2 (Frontend & User Experience)**, Stage 10 transforms isolated desktop preferences into a centralized, strongly typed, persistent system configuration plane.

```
+-----------------------------------------------------------------------------------------+
|                                    AUTONOM DESKTOP UI                                   |
|   +--------------------------+  +----------------------------------------------------+  |
|   |   SettingsNavigation     |  |   Active Settings Page (1 of 15 Categories)        |  |
|   |  - 15 Categories         |  |  - Grouped SettingsSection cards                   |  |
|   |  - Search & Status Badges|  |  - Form controls (SettingsField, SettingsToggle)   |  |
|   |  - Dirty state tracking  |  |  - SettingsSaveBar (Dirty state / Discard / Save)  |  |
|   +--------------------------+  +----------------------------------------------------+  |
+--------------------------------------------|--------------------------------------------+
                                             | TanStack Query / JSON Fetch
                                             v
+-----------------------------------------------------------------------------------------+
|                               FASTAPI LOCAL BACKEND (8765)                              |
|   +--------------------------+  +----------------------------------------------------+  |
|   | REST Endpoints           |  | SettingsRepository & Service                       |  |
|   | - /api/v1/settings/all   |  | - Pydantic Schema Validation (13 category models)  |  |
|   | - /api/v1/settings/{cat} |  | - Optimistic Concurrency & Partial Updates         |  |
|   | - /api/v1/settings/schema|  | - Security Audit Logging on Sensitive Changes      |  |
|   | - /api/v1/settings/export|  | - Safe JSON Export & Validated Import               |  |
|   +--------------------------+  +----------------------------------------------------+  |
+--------------------------------------------|--------------------------------------------+
                                             |
                     +-----------------------+-----------------------+
                     v                                               v
+------------------------------------------+    +-----------------------------------------+
|           SQLITE DATABASE (WAL)          |    |       WINDOWS DPAPI SECURE VAULT        |
| - `app_settings` (key, JSON, updated_at) |    | - Cryptographic User-Scope Key Wrapping |
| - `audit_events` (immutable action log)  |    | - `credential_references` (AES-256-GCM) |
+------------------------------------------+    +-----------------------------------------+
```

---

## 2. Information Architecture (15 Categories)

The Settings workspace is organized into 15 logical sections accessible via sub-routes `/settings/:category`:

| #   | Route                     | Category Name            | Scope             | Backend Persistence             | Native Host Integration       |
| --- | ------------------------- | ------------------------ | ----------------- | ------------------------------- | ----------------------------- |
| 1   | `/settings/general`       | General                  | Desktop / Global  | SQLite `settings:general`       | Date/time localization        |
| 2   | `/settings/appearance`    | Appearance               | Desktop UI        | SQLite `settings:appearance`    | ThemeContext & data-density   |
| 3   | `/settings/ai`            | AI Providers & Models    | Engine Gateway    | SQLite `settings:ai`            | RTX 4050 6GB VRAM bounds      |
| 4   | `/settings/agents`        | Agent Preferences        | Multi-Agent Swarm | SQLite `settings:agents`        | Concurrency & timeouts        |
| 5   | `/settings/automation`    | Automation & Tasks       | Worker Pool       | SQLite `settings:automation`    | Max workers & queue depth     |
| 6   | `/settings/permissions`   | Permissions & Autonomy   | Security Engine   | SQLite `settings:permissions`   | Hardware killswitch (`Pause`) |
| 7   | `/settings/computer`      | Computer Control         | OS Automation     | SQLite `settings:computer`      | Window bounds & UIA masks     |
| 8   | `/settings/integrations`  | Connected Services & MCP | Connectors        | SQLite `settings:integrations`  | Windows DPAPI Keystore        |
| 9   | `/settings/recruitment`   | Recruitment Preferences  | Career Engine     | SQLite `settings:recruitment`   | ATS threshold & quotas        |
| 10  | `/settings/storage`       | Storage & Data           | Persistence       | SQLite `settings:storage`       | SQLite snapshots & backups    |
| 11  | `/settings/notifications` | Notifications            | Windows Alerts    | SQLite `settings:notifications` | Windows Action Center toasts  |
| 12  | `/settings/desktop`       | Desktop & Startup        | Windows Shell     | SQLite `settings:desktop`       | Win32 Startup & System Tray   |
| 13  | `/settings/security`      | Security & Privacy       | Core Security     | SQLite `settings:security`      | DPAPI Vault & Local-first     |
| 14  | `/settings/diagnostics`   | Diagnostics & Health     | Observability     | Live probes & telemetry         | Process supervisor status     |
| 15  | `/settings/about`         | About & Updates          | System Meta       | Live versions & metadata        | Tauri runtime mode            |

---

## 3. Data Flows & Concurrency Control

1. **Initial Load**:
   - `SettingsWorkspace` issues `GET /api/v1/settings/all`.
   - The backend `SettingsRepository` loads stored JSON payloads from the `app_settings` SQLite table and merges them with default Pydantic model instances.
   - If a new setting field was added in a software update, default values are seamlessly backfilled without overwriting existing customized values.

2. **Dirty-State Management**:
   - As the user modifies form controls, changes are captured in `draftSettings`.
   - Categories containing modified values are flagged in `dirtyCategories`, highlighting the category item in the navigation pane and displaying the sticky `SettingsSaveBar`.
   - The user can click **Discard Changes** to revert `draftSettings` to the server state, or **Save Preferences** to dispatch updates.

3. **Validation & Atomic Persistence**:
   - Upon clicking save, a `PATCH /api/v1/settings/{category}` request is dispatched with the updated category payload.
   - FastAPI parses the payload through the category's specific Pydantic model (`GeneralSettings`, `AISettings`, etc.).
   - If validation fails (e.g., negative timeout, worker count > 8, out-of-range port), HTTP 400 is returned with a descriptive error message.
   - On success, the JSON is persisted to SQLite, updated timestamps are recorded, and sensitive changes (`permissions`, `security`, `automation`) generate immutable records in `audit_events`.

---

## 4. Portability: Non-Sensitive Export & Import

AUTONOM supports exporting configuration for backup or workstation migration while strictly protecting user secrets:

- **Safe Export (`GET /api/v1/settings/export`)**:
  - Packages non-sensitive configuration across all 13 categories into a versioned JSON document.
  - Strictly omits API keys, bearer tokens, passwords, and private SQLite data.
- **Validated Import (`POST /api/v1/settings/import`)**:
  - Validates incoming JSON structure against schema versioning.
  - Iterates through categories, parsing each against its Pydantic model.
  - Rejects malformed or untrusted properties.
  - Records an audit event upon successful import.
