# AUTONOM — Architecture Decision Records (ADRs)

## ADR-0001: Monorepo Structure & Separation of Concerns

### Context

AUTONOM combines a high-performance Windows desktop UI, native OS bridges, and an asynchronous multi-agent automation backend. We need an architecture that isolates native/desktop concerns from AI orchestration and allows independent testing and compilation.

### Decision

Adopt a structured monorepo:

- `apps/desktop`: Tauri 2.x + React 19 + TypeScript + Vite. Handles the user interface, window management, system tray, and local rendering.
- `services/agent_backend`: Python 3.11+ FastAPI service. Hosts the multi-agent runtime, LLM gateway, scraping pipelines, computer-use interaction engines, and SQLite storage.
- `packages/shared`: Shared TypeScript types, schemas, and API definitions.
- `tests`: Unified test suite for Python, TypeScript, and end-to-end integration.

### Consequences

- Clean separation of concerns with strong boundary checks.
- Rapid frontend hot-reloading during development without restarting the Python backend.
- Python ecosystem access (Playwright, PyTorch/ONNX, OpenCV, LangChain/LlamaIndex primitives, pywinauto).

---

## ADR-0002: Technology Stack Selection

### Context

AUTONOM requires low latency, information-dense rendering, low memory footprint, and native Windows integration.

### Decision

1. **Frontend**: React 19 with Vite and TypeScript. Styling via custom Tailwind CSS tokens adhering strictly to the dark AUTONOM dashboard specification (restrained blue `#2563eb` and cyan `#06b6d4` accents; no purple gradients or oversized decorative pills).
2. **Desktop Shell**: Tauri 2.x with Rust. Much lighter memory footprint (<50MB vs >150MB for Electron) and direct access to native Windows APIs via `windows-rs`.
3. **Backend Engine**: Python 3.11+ with FastAPI and `asyncio`. Provides non-blocking execution of agent loops, native Playwright support, and interoperability with AI/ML libraries.
4. **Package & Environment Management**: `pnpm` for frontend packages; `uv` for lightning-fast Python virtual environment and dependency isolation.

### Consequences

- High responsiveness and sub-second cold starts.
- Predictable and fast package installations.

---

## ADR-0003: SQLite with Write-Ahead Logging (WAL) for Local Persistence

### Context

AUTONOM is a local-first desktop application that must persist user career profiles, job listings, application histories, and immutable audit logs without requiring a cloud database server or external daemon.

### Decision

Use local SQLite 3 with `aiosqlite`:

- `PRAGMA journal_mode = WAL;` (enables concurrent readers and writers without blocking).
- `PRAGMA synchronous = NORMAL;` (optimal balance of persistence safety and write throughput).
- `PRAGMA foreign_keys = ON;` (strict relational integrity).
- Sensitive columns (tokens, passwords) encrypted using AES-256-GCM backed by Windows DPAPI.

### Consequences

- Zero external database installation required by user.
- Complete data privacy and offline capability.
- High transaction throughput suitable for logging agent actions in real time.

---

## ADR-0004: Dual-Modality Computer Interaction (Visual & Structural)

### Context

Autonomous job application submission and desktop automation encounter diverse software: standard web pages, complex SPAs, custom canvas widgets, native desktop dialogs, and legacy applications. No single interaction method succeeds universally.

### Decision

Implement a hybrid dual-modality interaction system:

1. **Structural Interaction (Primary)**:
   - Web: Playwright DOM querying, element inspection, and value setting.
   - Desktop: Windows UI Automation (UIA) COM client reading accessibility trees, control patterns, and automation IDs.
2. **Visual Interaction (Fallback & Verification)**:
   - High-speed desktop screen capture (DXGI Desktop Duplication API).
   - Vision-model grounding and OCR for bounding box coordinate resolution.
   - Human-like mouse movement curves (Bézier trajectories) and SendInput keyboard injection.

### Consequences

- Maximizes automation reliability: structural interaction where elements are identifiable; visual interaction when DOM/UIA trees are obscured or custom-rendered.
- Provides independent visual verification of structural actions.

---

## ADR-0005: Advance Authorization Matrix & Human-in-the-Loop Governance

### Context

Autonomous agents performing real-world actions (submitting applications, interacting with career portals, sending communications) can produce unintended side effects if completely unchecked.

### Decision

Implement a configurable 3-tier autonomy policy:

- **Tier 1 (Discovery & Analysis)**: Fully autonomous (e.g., job scanning, match scoring).
- **Tier 2 (Preparation & Drafting)**: Autonomous with user visibility (e.g., tailoring resumes, filling draft forms).
- **Tier 3 (Binding & Irreversible Actions)**: Mandatory human-in-the-loop approval modal (e.g., final application submission, sensitive attestations, payment flows).
- Strict non-fabrication constraint: Zero hallucination of user experience, degrees, or skills.

### Consequences

- High user trust and compliance with external service terms.
- Eliminates risk of unwanted application submissions.

---

## ADR-0006: Dual Windows Linker & Toolchain Strategy (MSVC / GNU)

### Context

Compiling native Windows Rust applications with Tauri 2 requires a C/C++ linker and system libraries. On developer machines without full Microsoft Visual Studio C++ Build Tools installed, standard `stable-x86_64-pc-windows-msvc` toolchain fails with `link.exe not found`.

### Decision

Support both Windows toolchains transparently:

1. `stable-x86_64-pc-windows-msvc` when Visual Studio Build Tools are installed.
2. `stable-x86_64-pc-windows-gnu` paired with MinGW-W64 GCC (`C:\Strawberry\c\bin\gcc.exe` or system MinGW) as a fast, self-contained fallback.
   Setup and test scripts (`setup.ps1`, `test.ps1`, `check.ps1`) dynamically discover and configure available linkers.

### Consequences

- Enables immediate compilation on standard Windows developer environments without requiring 5+ GB Visual Studio installation.
- Preserves native Win32 API access and Tauri 2 WebView2 integration.

---

## ADR-0007: In-Memory Async Pub/Sub EventBus & SSE Protocol

### Context

Desktop frontend clients require real-time visibility into asynchronous worker task progress, state transitions, and background agent operations. Using external brokers (Redis, RabbitMQ, Kafka) introduces heavy background service requirements inappropriate for a lightweight desktop app. Furthermore, standard bidirectional WebSockets introduce framing and reconnection complexity when client-to-server traffic is predominantly standard REST RPC.

### Decision

Implement an internal in-process asynchronous `EventBus` (`asyncio`) paired with Server-Sent Events (SSE) over HTTP (`GET /api/v1/events/stream`).

1. Publishers broadcast events non-blockingly (`put_nowait`).
2. Slow subscribers drop laggy frames rather than backpressuring active task workers.
3. An in-memory ring buffer retains the most recent 200 events for newly connected views.
4. SSE stream includes 15-second heartbeat pings and clean subscriber queue teardown on client disconnect.

### Consequences

- Zero external infrastructure dependencies or memory footprint.
- Built-in browser `EventSource` API handles auto-reconnect effortlessly.
- Full real-time diagnostic stream available to frontend clients without polling.

---

## ADR-0008: Cooperative Task Cancellation & Bounded Worker Concurrency

### Context

Long-running automation tasks (such as browser driving, computer control, or multi-step calculations) must be abortable by the user immediately. Thread termination or killing processes leaves unmanaged side effects, dangling browser windows, or corrupted state.

### Decision

Adopt cooperative cancellation mediated by `TaskExecutionContext`:

1. Tasks receive a context token and must routinely check `ctx.raise_if_cancelled()` or `ctx.is_cancelled()`.
2. Cancellation triggers a clean rollback in handlers before transitioning to `cancelled`.
3. Worker concurrency is strictly bounded (default 4 workers, 50 queue capacity) with immediate HTTP 429 backpressure rejection when saturated.

### Consequences

- Predictable, deterministic resource consumption aligned with the RTX 4050 / 16GB RAM budget.
- Clean resource cleanup on user abort without orphaned background operations.

---

## ADR-0009: SQLite Async Engine & Connection PRAGMAs for Single-Writer WAL Concurrency

### Context

AUTONOM is an asynchronous local desktop application requiring concurrent reads (dashboard UI, metrics, event streaming) while background workers perform write transactions (task state updates, scraping ingestion, audit logging). Default SQLite locking can result in `database is locked` errors during burst writes.

### Decision

Configure SQLAlchemy 2.x with `sqlite+aiosqlite` using mandatory connection PRAGMAs executed on every pooled connection:

1. `PRAGMA journal_mode = WAL;`: Enables Write-Ahead Logging, allowing concurrent readers to query without blocking the single writer.
2. `PRAGMA synchronous = NORMAL;`: Ensures durability without the severe write latency penalty of `FULL` synchronization.
3. `PRAGMA foreign_keys = ON;`: Enforces referential integrity across all 17 tables.
4. `PRAGMA busy_timeout = 10000;`: Provides a 10-second wait window for locks to clear before failing.

### Consequences

- Zero external server requirements while handling concurrent UI queries and worker writes seamlessly.
- Eliminates transient lock timeout errors under multi-agent load.

---

## ADR-0010: Windows DPAPI Envelope Encryption & Authenticated AES-256-GCM Vault

### Context

AUTONOM stores high-value user credentials (integration API keys, session tokens) and PII (contact email, phone numbers, home address). Storing secrets in plaintext in SQLite tables is a critical security vulnerability.

### Decision

Implement a two-tier envelope encryption architecture:

1. A 256-bit AES master key is generated via `os.urandom(32)` and protected directly by the Windows Data Protection API (`CryptProtectData` via Win32 `crypt32.dll`), tying decryption strictly to the active Windows user logon on that workstation.
2. Sensitive columns (such as applicant contact details and provider tokens) are encrypted using authenticated AES-256-GCM with a unique 96-bit random nonce and entity-bound Associated Data (AAD).
3. Plaintext secrets are never stored in SQLite, never logged, and masked in all public API responses.

### Consequences

- Defense-in-depth: copying the `.db` file to another computer or user account renders encrypted data cryptographically unreadable.
- Cryptographic tampering detection guaranteed by AES-GCM authentication tags.

---

## ADR-0011: Alembic Programmatic Migrations & Forward-Only Schema Versioning

### Context

In a desktop application deployed to end-user workstations, database schema updates must execute reliably during application startup without manual user intervention or destructive alterations.

### Decision

Use Alembic with asynchronous SQLAlchemy metadata:

1. Production desktop startup executes forward migrations programmatically (`init_database_schema` / `alembic upgrade head`).
2. Table alterations utilize Alembic's `batch_alter_table` mode to safely recreate SQLite tables without losing user data.
3. Pre-migration online snapshots are captured before schema modifications.

### Consequences

- Safe, non-destructive schema updates across application releases.
- Automated recovery path if a migration fails.

---

## ADR-0012: Online Database Backup API & Verified Restoration Workflow

### Context

Workstation crashes, sudden power loss, or accidental user actions could corrupt local persistent state. AUTONOM requires a robust point-in-time backup and verified recovery mechanism.

### Decision

Implement backup and restoration using SQLite's native Online Backup API (`sqlite3.backup`):

1. Captures consistent online snapshots without locking concurrent read operations.
2. Generates an independent `.manifest.json` recording backup metadata and SHA-256 checksums.
3. Before restoring, the backup file is validated with `PRAGMA integrity_check` in isolation and checksum comparison.
4. Captures an automatic safety snapshot (`pre_restore_safety_*.bak`) of the live database before overwriting.
5. Performs post-restore integrity checks and automatically rolls back if corruption is detected.

### Consequences

- True point-in-time disaster recovery with zero data loss risk during restoration.
- Automated FIFO retention limiting storage to the 10 most recent backups.

---

## ADR-0013: PyInstaller Standalone Sidecar Packaging for Zero-Prerequisite Desktop Distribution

### Context

AUTONOM requires Python for AI orchestration, FastAPI endpoints, and computer automation libraries. Expecting end users on Windows 11 to pre-install Python, setup virtual environments, and configure PATH variables is unacceptable for a consumer-facing desktop application.

### Decision

Package the Python FastAPI backend into a frozen, standalone single-file binary using PyInstaller (`autonom-api-x86_64-pc-windows-msvc.exe`) that bundles Python 3.12, Uvicorn, SQLAlchemy, aiosqlite, cryptography, and Alembic:

1. The desktop harness transparently discovers the binary in `<app>/bin/`.
2. A development-mode fallback allows running directly via `.venv/Scripts/python.exe` during local coding.
3. The packaged binary executes with `--host 127.0.0.1 --port 8765 --api-key <token>`.

### Consequences

- Zero Python prerequisite for end users.
- Fast startup and predictable dependency resolution.

---

## ADR-0014: Win32 Job Object Limits (`JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`) for Process Containment

### Context

If the desktop application terminates abruptly (Task Manager force-kill, sudden power loss, or host crash), child processes spawned by it (Python backend sidecar, worker processes, browser drivers) could be orphaned, holding open TCP ports and consuming CPU/RAM indefinitely.

### Decision

Use the native Windows Win32 Job Object API via `windows-sys`:

1. At Tauri startup, create an anonymous Win32 Job Object.
2. Configure `JOBOBJECT_EXTENDED_LIMIT_INFORMATION` with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`.
3. Assign each spawned sidecar process handle to the Job Object via `AssignProcessToJobObject`.

### Consequences

- The Windows operating system kernel unconditionally terminates the child backend process whenever the desktop process handle is closed.
- Eliminates orphaned child processes without relying on cooperative IPC.

---

## ADR-0015: Supervisor State Machine with Bounded Exponential Backoff Crash Recovery

### Context

Autonomous operations and local desktop automation can trigger transient failures, native library faults, or unhandled exceptions. A crashed backend should recover automatically without crashing the desktop UI or getting stuck in an infinite respawn loop.

### Decision

Implement a Rust-managed `BackendSupervisor` state machine (`Stopped`, `Starting`, `Connecting`, `Ready`, `Degraded`, `Restarting`, `Failed`, `Stopping`):

1. A background thread monitors the child process exit status.
2. Unexpected termination transitions state to `Restarting` and increments `restart_count`.
3. Bounded exponential backoff delay is enforced: $\Delta t = \min(1.0 \times 2^{\text{count}-1}, 16.0)\text{ s}$.
4. If `restart_count` exceeds 5, the state transitions to `Failed` and prompts user intervention.
5. Startup task reconciliation re-evaluates in-flight tasks from the durable SQLite database.

### Consequences

- Self-healing desktop runtime resilient to transient runtime faults.
- Prevents resource exhaustion from rapid crash-restart loops.

---

## ADR-0016: Tauri Native System Tray, Single-Instance Mutex, and Multi-Monitor Coordinate Validation

### Context

AUTONOM operates as an ambient autonomous assistant that runs in the background. Opening multiple copies could corrupt database locks, and saving window geometry across multiple displays could render the window off-screen if a display is disconnected.

### Decision

1. Enforce single-instance execution via `tauri-plugin-single-instance`, which detects existing instances via named mutex, restores/unhides the window, and focuses it.
2. Implement close-to-tray minimization with custom context menus (Open, Hide/Show, Status, Tasks, Restart, Exit).
3. Query `window.available_monitors()` before restoring saved geometry from `desktop_settings.json` and fall back to centered primary display if coordinates are out of bounds.

### Consequences

- Professional Windows 11 application ergonomics.
- Eliminates multi-instance database locking collisions and off-screen window bugs.
