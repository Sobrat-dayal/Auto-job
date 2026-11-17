# AUTONOM Permission & Risk Taxonomy Model

## 1. Permission Categories

AUTONOM categorizes all agent capabilities and tool operations into 10 structured permission categories:

```
                                 ┌─────────────────────────┐
                                 │   Permission Categories │
                                 └────────────┬────────────┘
         ┌───────────────┬────────────────────┼───────────────────┬──────────────┐
         ▼               ▼                    ▼                   ▼              ▼
    recruitment      filesystem            network           credential       browser
  (apply, match)  (read, write, del)  (http, api, scrape) (secrets, tokens) (nav, click)
         │               │                    │                   │              │
         ▼               ▼                    ▼                   ▼              ▼
      desktop      communication            code               creative        system
   (input, exec)   (email, telegram)   (lint, gen, run)   (media, 3d, svg) (daemon, proc)
```

1. **`recruitment`**: Job searching, criteria parsing, skill extraction, ATS application submission, recruiter message drafting, interview preparation.
2. **`filesystem`**: Canonical path operations, file reading, file creation, modification, and deletion.
3. **`network`**: External HTTP/HTTPS queries, webhook triggers, web scraping, and domain communications.
4. **`credential`**: Cryptographic keys, OAuth tokens, API keys, and session cookies managed via DPAPI/SQLite Vault.
5. **`browser`**: Headless/CDP browser navigation, form interaction, DOM extraction, and session handling.
6. **`desktop`**: Windows 11 UI automation, accessibility tree inspection, input synthesis, and process inspection.
7. **`communication`**: External email dispatch, chat messages (Telegram, Slack, WhatsApp), and calendar synchronization.
8. **`code`**: AST parsing, static analysis, code generation, compilation, and test execution.
9. **`creative`**: Asset synthesis, image processing, 3D glTF parsing, audio clipping, and report styling.
10. **`system`**: Background worker management, SQLite maintenance, database backup/restore, and health telemetry.

---

## 2. Risk Levels & Capability Mapping

Operations are assigned deterministic risk levels based on irreversible side effects, external visibility, and resource sensitivity:

```
  Risk Level   │ Characteristics                                   │ Default Action
 ──────────────┼───────────────────────────────────────────────────┼─────────────────────
  LOW          │ Read-only, analytical, parsing, local AST         │ Auto-Allow Baseline
  MODERATE     │ Local drafting, synthesis, non-destructive write │ Allow within Scope
  HIGH         │ External submissions, live email, file mutation   │ Require Approval
  CRITICAL     │ File deletion, database wipe, secret extraction   │ Mandatory Human Gate
```

### Risk Level Breakdown

| Capability / Action | Category | Risk Level | Authorization Default |
|---|---|---|---|
| `recruitment_match_skills` | `recruitment` | `LOW` | Auto-Allow Baseline |
| `recruitment_extract_job_requirements` | `recruitment` | `LOW` | Auto-Allow Baseline |
| `recruitment_draft_resume_bullets` | `recruitment` | `MODERATE` | Auto-Allow Baseline |
| `recruitment_submit_application` | `recruitment` | `HIGH` | Requires Human Approval |
| `email_send` | `communication` | `HIGH` | Requires Human Approval |
| `browser_submit_form` | `browser` | `HIGH` | Requires Human Approval |
| `desktop_execute_command` | `desktop` | `HIGH` | Requires Human Approval |
| `fs_modify_file` | `filesystem` | `HIGH` | Requires Human Approval |
| `fs_delete_file` | `filesystem` | `CRITICAL` | Mandatory Human Approval |
| `fs_delete_directory` | `filesystem` | `CRITICAL` | Mandatory Human Approval |
| `database_wipe_data` | `system` | `CRITICAL` | Mandatory Human Approval |
| `credential_read_secret` | `credential` | `CRITICAL` | Blocked (Security Invariant) |
