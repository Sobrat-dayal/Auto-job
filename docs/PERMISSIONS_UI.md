# AUTONOM — Action Permissions, Autonomy Matrix & Killswitch Architecture

## 1. Overview & Architectural Role

The Action Permissions system established in **Stage 10** represents the core safety and governance architecture of AUTONOM.

Because AUTONOM is designed to perform autonomous actions across the host operating system—such as web navigation, form submission, email correspondence, and file creation—the permission framework establishes strict user-controlled boundaries across 14 discrete operational categories.

```
+-----------------------------------------------------------------------------------------+
|                              FRONTEND: /settings/permissions                            |
| - Autonomy Preset Profiles (Strictly Supervised, Balanced Autonomous, Maximum Autonomy) |
| - 14-Category Action Permission Matrix (Interactive 3-Tier Autonomy Selectors)          |
| - Emergency Killswitch Configuration (Global Hotkey: `Pause`, Emergency Abort)          |
| - "Revoke All Pending Approvals" Action Button                                          |
+-----------------------------------------------------------------------------------------+
                                             |
                                             v PATCH /api/v1/settings/permissions
+-----------------------------------------------------------------------------------------+
|                               FASTAPI LOCAL BACKEND (8765)                              |
| - PermissionSettings Pydantic Schema Validation                                         |
| - Authorization Enforcement Middleware / Dependency                                     |
| - Audit Trail Dispatch (Records policy changes and authorization checks in SQLite WAL)  |
+-----------------------------------------------------------------------------------------+
                                             |
                     +-----------------------+-----------------------+
                     v                                               v
+------------------------------------------+    +-----------------------------------------+
|          SQLITE `app_settings`           |    |            TAURI NATIVE HOST            |
| - `matrix`: { action_id: tier }          |    | - Global Windows Hotkey Listener        |
| - `global_killswitch_hotkey`: "Pause"    |    |   (`Pause` / `Ctrl+Alt+Esc`)            |
| - `require_mfa_for_destructive`: true    |    | - Emergency Child Process Termination   |
+------------------------------------------+    +-----------------------------------------+
```

---

## 2. The 14-Category Action Permission Matrix

Every sensitive capability performed by an agent or workflow is mapped to one of 14 discrete permission categories:

| #   | Action Identifier  | Category Display Name   | Risk Profile     | Default Policy     | Description                                 |
| --- | ------------------ | ----------------------- | ---------------- | ------------------ | ------------------------------------------- |
| 1   | `job_discovery`    | Job Discovery & Search  | Low (Read)       | `always_allow`     | Scraping job boards and querying APIs       |
| 2   | `job_application`  | Application Submission  | High (Mutate)    | `require_approval` | Submitting candidate profiles or resumes    |
| 3   | `email_drafting`   | Email Draft Creation    | Low (Read/Draft) | `always_allow`     | Composing recruiter response drafts         |
| 4   | `email_sending`    | Recruiter Email Sending | High (External)  | `require_approval` | Dispatching outbound emails via SMTP/OAuth  |
| 5   | `fs_read`          | File System Read        | Low (Local)      | `always_allow`     | Reading workspace files, templates, resumes |
| 6   | `fs_write`         | File System Write       | Medium (Local)   | `always_allow`     | Saving generated PDFs, resumes, and reports |
| 7   | `shell_execution`  | Shell / CLI Execution   | High (System)    | `require_approval` | Running terminal commands or scripts        |
| 8   | `browser_nav`      | Browser Navigation      | Medium (Web)     | `always_allow`     | Visiting external URLs and inspecting DOM   |
| 9   | `input_simulation` | Mouse & Keyboard Input  | High (OS)        | `require_approval` | Simulating native Windows input events      |
| 10  | `screen_capture`   | Screen Capture & Vision | Medium (Privacy) | `always_allow`     | Capturing window screenshots for OCR/vision |
| 11  | `network_egress`   | External Network Egress | Medium (Network) | `always_allow`     | Outbound HTTP requests to permitted APIs    |
| 12  | `vault_access`     | Credential Vault Read   | Critical (Auth)  | `require_approval` | Accessing DPAPI-wrapped tokens or keys      |
| 13  | `settings_modify`  | System Configuration    | High (Config)    | `always_allow`     | Modifying application configuration         |
| 14  | `background_auto`  | Unattended Automation   | High (Workflow)  | `require_approval` | Scheduling recurring background runs        |

---

## 3. The Three Autonomy Tiers

Each action category must be assigned to one of three strictly enforced autonomy levels:

1. **`always_allow` (Autonomous)**:
   - The action executes immediately without presenting a modal or pausing the agent.
   - Operations are recorded in the security audit log for post-hoc review.
2. **`require_approval` (Human-in-the-Loop Supervised)**:
   - The agent prepares the exact action payload (e.g. application form contents, email text, CLI command) and halts.
   - A pending approval item is generated in the Command Center queue with full diff inspection.
   - Execution resumes only after the user clicks "Approve" or submits biometric/PIN confirmation.
3. **`never_allow` (Strictly Forbidden)**:
   - The capability is blocked at the backend authorization middleware.
   - Any agent attempting the operation receives a `403 Forbidden: ActionDisallowedByPolicy` error, prompting it to gracefully abort or adapt its plan.

---

## 4. Hardware Killswitch & Emergency Abort

To guarantee user safety and peace of mind when running autonomous agents, AUTONOM provides a multi-layer physical killswitch:

### 4.1 Native Global Hotkeys

- **Primary Killswitch (`Pause / Break`)**: Registered via the Tauri global shortcut API. Pressing `Pause` from any application immediately sends an emergency halt signal to `POST /api/v1/automation/pause`, suspending all worker threads.
- **Emergency Abort (`Ctrl+Alt+Esc`)**: Hard-terminates active browser instances (Playwright/Chrome), closes native input automation hooks, and resets worker state.

### 4.2 Software Killswitch

The UI header and [PermissionSettingsPage.tsx](file:///e:/proooo/AUTO%20JOB/apps/desktop/src/features/settings/pages/PermissionSettingsPage.tsx) provide:

- **"Revoke All Approvals"**: Instantly cancels all outstanding approval requests in the queue.
- **"Emergency Freeze"**: Locks the application into read-only mode until unlocked by user PIN or confirmation.

---

## 5. Global Policy Presets

To simplify configuration, the UI offers three pre-tuned autonomy profiles:

```typescript
export const AUTONOMY_PRESETS = {
  // Conservative: Human verifies all external or mutating actions
  supervised: {
    job_application: 'require_approval',
    email_sending: 'require_approval',
    shell_execution: 'never_allow',
    input_simulation: 'require_approval',
    vault_access: 'require_approval',
    background_auto: 'require_approval',
  },
  // Balanced: Standard operational default (supervised external impact)
  balanced: {
    job_application: 'require_approval',
    email_sending: 'require_approval',
    shell_execution: 'require_approval',
    input_simulation: 'always_allow',
    vault_access: 'require_approval',
    background_auto: 'always_allow',
  },
  // High Autonomy: Trusted local environment, minimal friction
  autonomous: {
    job_application: 'always_allow',
    email_sending: 'require_approval', // Remains supervised for safety
    shell_execution: 'always_allow',
    input_simulation: 'always_allow',
    vault_access: 'always_allow',
    background_auto: 'always_allow',
  },
};
```

---

## 6. Backend Authorization Enforcement

Every API endpoint performing protected operations validates permissions via FastAPI dependency injection:

```python
# services/api/app/core/permissions.py
async def require_permission(action: ActionType, db: Session = Depends(get_db)):
    settings = get_settings_repository(db).get_category("permissions")
    policy = settings.matrix.get(action, PermissionTier.REQUIRE_APPROVAL)

    if policy == PermissionTier.NEVER_ALLOW:
        raise HTTPException(
            status_code=403,
            detail=f"Action '{action}' is strictly forbidden by policy.",
        )
    elif policy == PermissionTier.REQUIRE_APPROVAL:
        # Halt execution and generate approval request in queue
        raise ActionRequiresApprovalException(action=action)

    # Audit log permitted action
    log_audit_event(action=action, status="PERMITTED")
```
