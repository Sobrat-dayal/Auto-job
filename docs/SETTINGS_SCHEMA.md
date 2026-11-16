# AUTONOM — Settings Schema & Registry Reference

## 1. Schema Design Principles

1. **Strict Type Safety**: All settings are modeled using Pydantic v2 schemas on the backend and aligned TypeScript interfaces in `@autonom/shared-types`.
2. **Explicit Bounded Limits**: Numeric fields enforce sensible physical and system boundaries (e.g., worker concurrency constrained to 1–8; VRAM allocation constrained to 1024–6144 MB).
3. **Restart Requirements**: Settings that affect thread pools, OS process bindings, or memory maps explicitly declare `requires_restart: true`.
4. **Zero-Plaintext Invariant**: No sensitive credentials (API keys, session cookies, passwords) are stored in plaintext in settings tables or returned in settings payloads. All secrets are managed exclusively by the Windows DPAPI encrypted vault.

---

## 2. Category Schemas & Parameters

### 2.1 General Settings (`settings:general`)

| Key                           | Type      | Default        | Constraints                              | Description                         |
| ----------------------------- | --------- | -------------- | ---------------------------------------- | ----------------------------------- |
| `app_language`                | `string`  | `"en-US"`      | Valid locale string                      | Application display language        |
| `date_format`                 | `enum`    | `"YYYY-MM-DD"` | `YYYY-MM-DD`, `DD/MM/YYYY`, `MM/DD/YYYY` | Date presentation format            |
| `time_format`                 | `enum`    | `"24h"`        | `24h`, `12h`                             | Clock presentation format           |
| `timezone_display`            | `enum`    | `"Local"`      | `Local`, `UTC`                           | Timezone representation             |
| `default_landing_page`        | `string`  | `"/dashboard"` | Valid route path                         | Default startup workspace route     |
| `confirm_destructive_actions` | `boolean` | `true`         | —                                        | Confirm before deleting records     |
| `confirm_backup_restore`      | `boolean` | `true`         | —                                        | Confirm before replacing SQLite DB  |
| `confirm_task_cancellation`   | `boolean` | `true`         | —                                        | Confirm before terminating workers  |
| `show_technical_metrics`      | `boolean` | `true`         | —                                        | Display hardware VRAM/latency in UI |
| `high_contrast_borders`       | `boolean` | `false`        | —                                        | Accessibility high-contrast borders |

### 2.2 Appearance Settings (`settings:appearance`)

| Key                        | Type      | Default         | Constraints              | Description                         |
| -------------------------- | --------- | --------------- | ------------------------ | ----------------------------------- |
| `theme`                    | `enum`    | `"navy-dark"`   | `navy-dark`, `dark`      | Visual theme palette                |
| `density`                  | `enum`    | `"comfortable"` | `comfortable`, `compact` | UI spacing and padding mode         |
| `font_scale`               | `enum`    | `"100%"`        | `90%`, `100%`, `110%`    | Root typography font multiplier     |
| `sidebar_default_expanded` | `boolean` | `true`          | —                        | Default expanded navigation sidebar |
| `reduced_motion`           | `boolean` | `false`         | —                        | Disable transition animations       |
| `chart_animations`         | `boolean` | `true`          | —                        | Animate Recharts transitions        |
| `table_density`            | `enum`    | `"normal"`      | `normal`, `compact`      | Table row vertical padding          |

### 2.3 AI Providers & Models (`settings:ai`)

| Key                            | Type                   | Default                             | Constraints         | Description                        |
| ------------------------------ | ---------------------- | ----------------------------------- | ------------------- | ---------------------------------- |
| `providers`                    | `list[AIProviderItem]` | `[Ollama, OpenAI, Anthropic]`       | Max 10 providers    | Configured provider endpoints      |
| `models`                       | `list[AIModelItem]`    | `[Llama 3.2 3B, Qwen 2.5 Coder 7B]` | Max 20 models       | Task-to-model assignments          |
| `single_active_model_enforced` | `boolean`              | `true`                              | Restart Required    | Single model loaded in VRAM        |
| `max_vram_allocation_mb`       | `int`                  | `5120`                              | `1024` to `6144` MB | VRAM budget ceiling (RTX 4050)     |
| `idle_model_unload_seconds`    | `int`                  | `300`                               | `30` to `3600` sec  | Release GPU memory when idle       |
| `cloud_fallback_enabled`       | `boolean`              | `false`                             | —                   | Route to cloud if VRAM constrained |

### 2.4 Agent Preferences (`settings:agents`)

| Key                       | Type                    | Default              | Constraints                                      | Description                       |
| ------------------------- | ----------------------- | -------------------- | ------------------------------------------------ | --------------------------------- |
| `agents`                  | `list[AgentConfigItem]` | 24 agent profiles    | —                                                | Agent timeouts and model bindings |
| `default_autonomy_level`  | `enum`                  | `"tier2_supervised"` | `tier1_full`, `tier2_supervised`, `tier3_manual` | Baseline autonomy tier            |
| `auto_retry_failed_tasks` | `boolean`               | `true`               | —                                                | Retry transient task failures     |
| `max_agent_retries`       | `int`                   | `2`                  | `0` to `5`                                       | Maximum retry attempts per task   |

### 2.5 Automation Settings (`settings:automation`)

| Key                             | Type      | Default | Constraints                      | Description                          |
| ------------------------------- | --------- | ------- | -------------------------------- | ------------------------------------ |
| `max_concurrent_workers`        | `int`     | `4`     | `1` to `8` (Restart Required)    | Parallel worker execution slots      |
| `max_queued_tasks`              | `int`     | `50`    | `10` to `200` (Restart Required) | Maximum bounded queue depth          |
| `task_default_timeout_seconds`  | `float`   | `60.0`  | `5.0` to `600.0` sec             | Global task watchdog timeout         |
| `retry_limit`                   | `int`     | `3`     | `0` to `10`                      | Worker retry limit                   |
| `background_dispatch_enabled`   | `boolean` | `true`  | —                                | Master background task switch        |
| `task_history_retention_days`   | `int`     | `30`    | `7` to `365` days                | Task history log retention           |
| `notify_on_task_failure`        | `boolean` | `true`  | —                                | Toast notification on job failure    |
| `pause_dispatch_on_error_spike` | `boolean` | `true`  | —                                | Circuit breaker on >50% failure rate |

### 2.6 Permissions Settings (`settings:permissions`)

| Key                           | Type                   | Default       | Constraints         | Description                           |
| ----------------------------- | ---------------------- | ------------- | ------------------- | ------------------------------------- |
| `permissions`                 | `list[PermissionRule]` | 14 categories | —                   | Granular action permission rules      |
| `emergency_killswitch_hotkey` | `string`               | `"Pause"`     | Valid hotkey string | Global hardware interrupt key         |
| `preauthorize_discovery`      | `boolean`              | `true`        | —                   | Preauthorize read-only job scouting   |
| `preauthorize_dossier_prep`   | `boolean`              | `true`        | —                   | Preauthorize tailoring resumes/covers |

### 2.7 Computer Control Settings (`settings:computer`)

| Key                               | Type        | Default                                                   | Constraints                                           | Description                            |
| --------------------------------- | ----------- | --------------------------------------------------------- | ----------------------------------------------------- | -------------------------------------- |
| `preferred_interaction_mode`      | `enum`      | `"structural_first"`                                      | `structural_first`, `visual_first`, `structural_only` | Windows UIA vs vision models           |
| `visual_fallback_enabled`         | `boolean`   | `true`                                                    | —                                                     | Vision fallback if UIA lacks labels    |
| `idle_capture_interval_seconds`   | `float`     | `5.0`                                                     | `1.0` to `60.0` sec                                   | Screenshot interval when idle          |
| `active_capture_interval_seconds` | `float`     | `1.0`                                                     | `0.5` to `10.0` sec                                   | Screenshot interval during tasks       |
| `burst_capture_interval_seconds`  | `float`     | `0.2`                                                     | `0.1` to `2.0` sec                                    | Burst capture during synthetic actions |
| `screenshot_retention_hours`      | `int`       | `24`                                                      | `1` to `168` hours                                    | Local debug screenshot retention       |
| `sensitive_region_redaction`      | `boolean`   | `true`                                                    | —                                                     | Mask passwords, banking fields         |
| `allowed_applications`            | `list[str]` | `[chrome, msedge, code, notepad]`                         | —                                                     | Permitted Win32 process names          |
| `blocked_applications`            | `list[str]` | `[regedit, cmd, powershell, taskmgr, keepass, 1password]` | —                                                     | Blocked Win32 process names            |
| `mouse_keyboard_control_enabled`  | `boolean`   | `false`                                                   | Hard disabled in Stage 10                             | Synthetic SendInput events             |
| `session_timeout_minutes`         | `int`       | `30`                                                      | `5` to `240` min                                      | Maximum control session duration       |

### 2.8 Recruitment Settings (`settings:recruitment`)

| Key                                     | Type         | Default                              | Constraints                            | Description                      |
| --------------------------------------- | ------------ | ------------------------------------ | -------------------------------------- | -------------------------------- |
| `desired_job_titles`                    | `list[str]`  | `[Software Engineer, Full Stack...]` | Non-empty strings                      | Target job titles to scout       |
| `role_levels`                           | `list[enum]` | `[entry, mid]`                       | `internship, entry, mid, senior, lead` | Seniority levels                 |
| `preferred_locations`                   | `list[str]`  | `[Remote, Bengaluru, SF...]`         | —                                      | Target geographic regions        |
| `work_style`                            | `list[enum]` | `[remote, hybrid]`                   | `remote, hybrid, onsite`               | Work arrangement preferences     |
| `max_daily_applications`                | `int`        | `5`                                  | `1` to `25` apps/day                   | Quota ceiling for submissions    |
| `minimum_match_threshold`               | `int`        | `75`                                 | `50` to `100` %                        | Minimum ATS score to apply       |
| `resume_tailoring_mode`                 | `enum`       | `"focused"`                          | `subtle, focused, comprehensive`       | Keyword tailoring depth          |
| `require_human_approval_for_submission` | `boolean`    | `true`                               | Tier 2 gate                            | Human review before submitting   |
| `auto_submission_authorized`            | `boolean`    | `false`                              | Planned Stage 31                       | Direct submission without review |

### 2.9 Storage Settings (`settings:storage`)

| Key                         | Type      | Default | Constraints         | Description                       |
| --------------------------- | --------- | ------- | ------------------- | --------------------------------- |
| `backup_retention_count`    | `int`     | `10`    | `3` to `50` backups | Number of database snapshots kept |
| `data_retention_days`       | `int`     | `90`    | `7` to `365` days   | Diagnostic records retention      |
| `auto_backup_on_startup`    | `boolean` | `true`  | —                   | Snapshot on desktop launch        |
| `auto_vacuum_enabled`       | `boolean` | `true`  | —                   | Incremental SQLite vacuum         |
| `artifact_storage_limit_mb` | `int`     | `2048`  | `512` to `20480` MB | Disk quota for tailored PDFs      |

### 2.10 Notification Settings (`settings:notifications`)

| Key                          | Type      | Default | Constraints | Description                        |
| ---------------------------- | --------- | ------- | ----------- | ---------------------------------- |
| `notifications_enabled`      | `boolean` | `true`  | —           | Master notification switch         |
| `notify_on_task_completion`  | `boolean` | `true`  | —           | Toast on job success               |
| `notify_on_task_failure`     | `boolean` | `true`  | —           | Toast on job failure               |
| `notify_on_pending_approval` | `boolean` | `true`  | —           | Toast when human sign-off needed   |
| `notify_on_backend_events`   | `boolean` | `true`  | —           | Toast on sidecar supervisor events |
| `quiet_hours_enabled`        | `boolean` | `false` | —           | Suppress sound/popups during hours |
| `sound_enabled`              | `boolean` | `true`  | —           | Play notification audio chime      |
| `mask_sensitive_previews`    | `boolean` | `true`  | —           | Omit names/salaries from toasts    |

### 2.11 Desktop & Startup Settings (`settings:desktop`)

| Key                          | Type      | Default | Constraints          | Description                          |
| ---------------------------- | --------- | ------- | -------------------- | ------------------------------------ |
| `start_at_login`             | `boolean` | `false` | Windows Registry Run | Launch AUTONOM on Windows boot       |
| `close_to_tray`              | `boolean` | `true`  | —                    | Closing window hides to tray         |
| `minimize_to_tray`           | `boolean` | `true`  | —                    | Minimizing window hides to tray      |
| `restore_window_position`    | `boolean` | `true`  | Multi-monitor bounds | Remember window coordinates          |
| `auto_start_backend_sidecar` | `boolean` | `true`  | Win32 Job Object     | Supervise Python FastAPI process     |
| `max_backend_restarts`       | `int`     | `5`     | `1` to `20` restarts | Max restarts before supervisor halts |

### 2.12 Security & Privacy Settings (`settings:security`)

| Key                       | Type      | Default         | Constraints                                  | Description                         |
| ------------------------- | --------- | --------------- | -------------------------------------------- | ----------------------------------- |
| `dpapi_vault_enabled`     | `boolean` | `true`          | Windows DPAPI                                | Cryptographic key wrapping          |
| `redact_secrets_in_logs`  | `boolean` | `true`          | Regex patterns                               | Replace API keys with [REDACTED]    |
| `audit_logging_level`     | `enum`    | `"all_actions"` | `all_actions, sensitive_only, security_only` | Immutable audit logging detail      |
| `local_first_strict_mode` | `boolean` | `true`          | Loopback boundary                            | Block outbound net without provider |
| `telemetry_enabled`       | `boolean` | `false`         | Local only                                   | Diagnostic telemetry                |
