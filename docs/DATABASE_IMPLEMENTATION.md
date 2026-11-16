# AUTONOM — Persistent Database Architecture & Implementation

## 1. Overview & Architectural Principles

AUTONOM employs an asynchronous, local-first relational database architecture powered by **SQLite 3** via **SQLAlchemy 2.x** and **aiosqlite**. The design strictly adheres to the following principles:

1. **Local-First & Zero External Daemons**: Runs entirely on the user's Windows 11 workstation without requiring Postgres, MySQL, Redis, or external database processes.
2. **Single-Writer, Concurrent-Reader Concurrency**: Configured in SQLite Write-Ahead Logging (`WAL`) mode, allowing multiple asynchronous read transactions to execute concurrently alongside a single write transaction without blocking.
3. **Strict Relational Integrity**: Enforced foreign key constraints (`PRAGMA foreign_keys = ON;`) on every pooled connection to eliminate orphaned records across task events, profile evidence, and application attempts.
4. **Busy Timeout Resilience**: A 10,000 millisecond busy timeout (`PRAGMA busy_timeout = 10000;`) prevents transient `database is locked` errors during burst write operations.
5. **Separation of Metadata and Large Artifacts**: Large binary payloads (PDF resumes, portfolio screenshots, audio files) are stored on the local filesystem (`%LOCALAPPDATA%\AUTONOM\artifacts\`), while the SQLite database stores indexed metadata, file paths, SHA-256 hashes, and structured relations.

---

## 2. Directory Layout & Storage Topology

All database files and persistent assets are contained within the designated Windows AppData directory:

```
%LOCALAPPDATA%\AUTONOM\
├── database/
│   ├── autonom.db          # Primary SQLite database file
│   ├── autonom.db-wal      # Write-Ahead Log file (active transactions)
│   └── autonom.db-shm      # Shared-memory index for WAL mode
├── config/
│   └── .vault.key          # 256-bit AES master key wrapped with Windows DPAPI
├── backups/
│   ├── backup_*.db         # Consistent online backup snapshots
│   └── backup_*.manifest.json # Cryptographic backup verification manifests
├── artifacts/
│   └── (resumes, screenshots, generated documents)
├── logs/
│   └── autonom.log         # Rotated diagnostic logs
└── cache/
    └── (ephemeral temporary files eligible for automated purging)
```

---

## 3. SQLite Connection PRAGMAs

On every connection established through SQLAlchemy's `AsyncEngine`, the following PRAGMAs are executed synchronously via the connection pool's `connect` event listener (`app/db/engine.py`):

```sql
PRAGMA journal_mode = WAL;          -- Enables concurrent readers during active writes
PRAGMA synchronous = NORMAL;        -- Safe persistence with high write throughput in WAL mode
PRAGMA foreign_keys = ON;           -- Enforces referential integrity on all foreign key relations
PRAGMA busy_timeout = 10000;        -- Waits up to 10 seconds for locks to clear before failing
PRAGMA temp_store = MEMORY;         -- Evaluates temporary tables and query sorting in RAM
```

---

## 4. Relational Schema Architecture (17 Tables)

The database schema is partitioned into six functional domain groupings implemented in `app/db/models.py`:

### Group A: System & Configuration

- **`app_settings`**: Key-value JSON storage for user and system configurations (themes, autonomy limits, default timeouts). Keyed by string primary key `key`, with `value_json`, `schema_version`, and `scope`.

### Group B: Applicant Profiles & Career Portfolio

- **`applicant_profiles`**: Master applicant identity containing target roles, summary, career preferences, and an encrypted binary/text blob `contact_info_encrypted` protected by the DPAPI vault.
- **`verified_skills`**: Granular career skills with years of experience, proficiency rating, and verification sources linked to an applicant profile.
- **`profile_evidence`**: Verifiable proof points (GitHub repos, patents, publications, certifications) linked to profiles and skills.
- **`resume_versions`**: Generated and imported resume versions containing structured JSON content, raw text, rendered artifact references, target role tags, and ATS scoring benchmarks.

### Group C: Job Sourcing & Opportunities

- **`job_sources`**: Ingestion channels (LinkedIn, Indeed, Greenhouse, Lever, Workday) with scrape intervals and health status.
- **`job_listings`**: Discovered job opportunities with unique composite constraints (`source_id`, `external_job_id`) or URL deduplication, company, salary ranges, location, requirements, and expiration status.
- **`job_matches`**: Semantic compatibility scoring between applicant profiles and job listings, containing fit scores, match rationales, missing skills, and review decisions.

### Group D: Application Lifecycle

- **`applications`**: Formal job applications tracking state (`draft`, `queued`, `submitted`, `interviewing`, `rejected`, `offered`).
- **`application_attempts`**: Individual automated or manual submission attempts, tracking HTTP responses, browser interaction traces, submitted resume IDs, screening answers, and failure diagnostics.

### Group E: Task Execution & Worker Management

- **`tasks`**: Durable records of all agent and worker tasks with UUID primary key `id`, `task_type`, `priority`, `status`, `progress`, `progress_message`, payload JSON, result JSON, error details JSON, and correlation IDs.
- **`task_events`**: Immutable audit log of state transitions (`task.created`, `task.started`, `task.progress`, `task.completed`, `task.failed`), with transition timestamps and payload deltas.
- **`worker_runs`**: Execution log of worker threads/processes, recording worker IDs, assigned tasks, duration, CPU/memory samples, and completion status.
- **`agent_definitions`**: Catalog of the 24 AUTONOM agent specifications (prompt templates, tool access lists, autonomy tiers, LLM model preferences).

### Group F: Secure Vault, Artifacts & Audit Trail

- **`artifacts`**: Registry of on-disk binary artifacts (resumes, screenshots, exports) tracking file path, MIME type, SHA-256 checksum, size, and source task ID.
- **`credential_references`**: Pointers to external credentials (API keys, session cookies). **Plaintext secrets are never stored here**; secrets are encrypted by the DPAPI/AES-256-GCM vault, with only metadata and encrypted payloads recorded.
- **`audit_events`**: Append-only compliance log recording critical human-in-the-loop decisions, credential accesses, and destructive actions.

---

## 5. Repository Layer Architecture

Business logic interacts with the database exclusively through typed repositories in `app/repositories/`:

- **`SettingsRepository`**: Safe JSON configuration reads, updates, and schema validation.
- **`ProfileRepository`**: Handles transparent encryption and decryption of sensitive contact details using the security vault, preventing plaintext exposure.
- **`JobRepository`**: Idempotent insertion of job listings, detecting duplicates via SHA-256 URL hashing and external IDs.
- **`TaskRepository`**: Manages task creation, atomic state transitions, timeout checks, and startup reconciliation for interrupted jobs.
- **`TaskEventRepository`**: Durable append-only event recording.
- **`CredentialRepository`**: Secure credential storage, masking, and revocation.
- **`ArtifactRepository`**: File artifact registration and checksum verification.
- **`AuditRepository`**: Tamper-evident logging of security-sensitive operations.

---

## 6. Startup State Reconciliation

When the AUTONOM backend process launches:

1. `service_container.py` invokes `TaskExecutionManager.load_persisted_tasks()`.
2. The repository queries for tasks left in non-terminal active states (`Running`, `Queued`, `Paused`) from a previous process crash or sudden Windows shutdown.
3. These tasks are automatically transitioned to `Failed` with diagnostic reason:
   ```
   INTERRUPTED: Process stopped unexpectedly while task was active.
   ```
4. A durable `task.failed` event is appended to `task_events`.
5. The manager's in-memory cache is populated with recent tasks for instant dashboard display.
