# AUTONOM — Data Retention, Lifecycle & Storage Governance

## 1. Data Classification Model

AUTONOM classifies all stored data into four distinct tiers based on user criticality, security sensitivity, and durability requirements:

| Classification                    | Retention Period               | Storage Location                                                                           | Purge / Prune Policy                                              | Example Assets                                                         |
| :-------------------------------- | :----------------------------- | :----------------------------------------------------------------------------------------- | :---------------------------------------------------------------- | :--------------------------------------------------------------------- |
| **Tier 1: Permanent Core**        | Indefinite (User-controlled)   | SQLite Tables (`app_settings`, `applicant_profiles`, `verified_skills`, `resume_versions`) | Explicit user deletion only                                       | Career history, contact details, tailored resumes, application records |
| **Tier 2: Operational History**   | 90 days default (Configurable) | SQLite Tables (`tasks`, `task_events`, `worker_runs`, `job_matches`, `audit_events`)       | Automated archival / prune older than 90 days                     | Detailed agent task events, match scores, execution metrics            |
| **Tier 3: Snapshots & Backups**   | 10 most recent snapshots       | `%LOCALAPPDATA%\AUTONOM\backups\`                                                          | FIFO prune: oldest deleted when total exceeds 10                  | Point-in-time `.db` snapshots and `.manifest.json` files               |
| **Tier 4: Ephemeral & Transient** | 48 hours max                   | `%LOCALAPPDATA%\AUTONOM\cache\`                                                            | Periodic sweep; deleted at process startup or via cleanup utility | Temporary web downloads, intermediate OCR frames, render buffers       |

---

## 2. Retention Policies by Entity

### 1. Applicant Profiles & Resumes (Tier 1)

- **Retention**: Never automatically purged.
- **Data Subject Rights**: When an applicant profile is deleted by the user, all related `verified_skills`, `profile_evidence`, `job_matches`, and `resume_versions` are removed in an atomic cascading transaction (`ON DELETE CASCADE`).

### 2. Job Listings & Scraped Postings (Tier 2)

- **Active Postings**: Retained while the posting is active on the source portal.
- **Expired Postings**: Marked `is_expired = True`. Retained for 60 days to prevent duplicate re-discovery, then eligible for background pruning if not tied to an active application.

### 3. Task Execution Records & Event Audit Trail (Tier 2)

- **Task Summary**: `tasks` records are retained for 90 days to provide long-term reporting on application success rates and agent performance.
- **Detailed Events**: `task_events` transitions are retained alongside tasks. Completed tasks older than 90 days can be archived or compacted.

### 4. Binary Artifacts (Tier 1 & Tier 4)

- **Permanent Artifacts** (Saved PDF resumes, cover letters, application receipts): Retained indefinitely while referenced in `artifacts` and `applications`.
- **Ephemeral Artifacts** (Transient screen captures for visual grounding, temporary DOM dumps): Automatically assigned a 48-hour expiration timestamp and purged during daily maintenance sweeps.

---

## 3. Storage Maintenance Utilities

The backend maintenance service (`app/db/maintenance.py`) exposes programmatic and automated cleanup:

```python
def cleanup_expired_data(max_cache_age_hours: int = 48) -> dict[str, int]:
    """Cleans temporary cache files without touching permanent user records or active tasks."""
    ...
```

- **Frequency**: Executed on startup and scheduled daily during idle periods.
- **Safety**: Never touches `database/`, `config/`, or permanent `artifacts/` subdirectories.
