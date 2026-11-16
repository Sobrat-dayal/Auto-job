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

---

## ADR-0017: Dark High-Density Windows 11 Design System with Restrained Blue/Cyan Accents

### Context

AUTONOM is an autonomous agent supervisory workstation rather than a consumer web app or marketing portal. It requires an information-dense interface that reduces operator cognitive fatigue during prolonged oversight sessions. Prior consumer design tropes (such as saturated neon glows, purple/gold gradients, oversized rounded pills, and marketing hero banners) distract operators and diminish information density.

### Decision

Establish a disciplined dark dashboard design language inspired by modern Windows 11 system utilities, developer workstations, and financial terminals:

1. Base canvas `#0B1220`, secondary surface `#121E30`, elevated containers `#1B2B42`, and border boundaries `#2A3A52`.
2. Restrained semantic accents: primary action blue `#338BDF` and electric cyan `#51C8E8`.
3. Typography scale built on Segoe UI Variable, with tabular figures (`tnum`) for real-time counters and dedicated technical monospace for hashes, process IDs, and addresses.
4. Total elimination of consumer marketing cards, decorative pill buttons, and saturated neon gradients.

### Consequences

- Clear visual hierarchy and high information throughput for multi-agent supervisory operations.
- Professional, restrained desktop aesthetic consistent with Windows 11.

---

## ADR-0018: Radix UI Primitives with Class Variance Authority (CVA) for Component Architecture

### Context

Building a component library for an autonomous desktop workstation requires strict accessibility (WCAG 2.2 AA), reliable keyboard navigation, predictable variant management, and zero runtime CSS overhead.

### Decision

Construct the AUTONOM React component library on unstyled `@radix-ui/react-*` accessible primitives combined with `class-variance-authority` (CVA) and Tailwind CSS:

1. Radix UI provides headless, battle-tested accessibility foundations (focus trapping, focus restoration, ARIA attributes, escape-key handling, arrow navigation).
2. CVA provides type-safe prop-to-class variant mappings (`variant`, `size`, `hasError`, `isLoading`).
3. Standardized component directory structure under `components/ui/`, `components/layout/`, `components/data-display/`, `components/charts/`, and `components/feedback/`.

### Consequences

- 100% WCAG 2.2 AA compliant components out-of-the-box.
- Type-safe variant APIs across all interactive controls.
- Consistent styling without CSS-in-JS runtime overhead.

---

## ADR-0019: TanStack Table v8 for High-Performance Desktop Operational Grids

### Context

Autonomous agent workflows produce high volumes of tabular data (scouted jobs, match scores, execution logs, backup manifests, system events). The frontend requires a fast, customizable data grid supporting client-side filtering, multi-column sorting, and virtualization without opinionated styling constraints.

### Decision

Adopt TanStack Table v8 (`@tanstack/react-table@8.20.6`) for all operational tables:

1. Headless architecture provides total control over DOM structure, density scaling, and dark theme classes.
2. Built-in global search filtering and multi-column sorting.
3. Pagination controls integrated with accessible ARIA navigation buttons.

### Consequences

- High throughput rendering of streaming agent tables.
- Zero layout jank when switching between comfortable and compact densities.

---

## ADR-0020: Dual-Density System (Comfortable vs. Compact) with Local Persistence

### Context

Operators supervise AUTONOM on varying display configurations: standard laptop screens (1080p, 125% DPI) require comfortable touch/click targets, whereas high-resolution multi-monitor setups (4K, 100% DPI, ultrawide) demand compact information-dense grids to maximize simultaneous agent visibility.

### Decision

Implement a dynamic density system driven by `data-density="comfortable"` and `data-density="compact"` attributes on `<html>`:

1. Density alters CSS custom properties (`--density-input-height`, `--density-card-padding`, `--density-table-row-height`).
2. `ThemeProvider` exposes `useDensity()` and `toggleDensity()` with instant persistence to `localStorage.getItem('autonom_density')`.
3. Quick-toggle pill button integrated into the global desktop header.

### Consequences

- Seamless transition between comfortable laptop mode and compact multi-agent workstation mode.
- User preference persists across application restarts.

---

## ADR-0021: Dual-Mode Expandable & Collapsible Desktop Navigation Architecture

### Context

AUTONOM is an autonomous multi-agent platform where operators primarily supervise background tasks rather than conducting manual data entry. The desktop navigation must allow rapid context-switching between 16 top-level functional modules and 50+ child sub-routes without permanently sacrificing horizontal viewport space on laptops or compact windows.

### Decision

Implement a dual-mode expandable and collapsible sidebar (`AppSidebar.tsx`):

1. **Mode A (Expanded)**: Fixed width `240px` (`w-60 min-w-[240px]`), showing full brand header, 5 category groups (`MAIN`, `RECRUITMENT`, `WORKSPACE`, `MANAGEMENT`, `DEVELOPMENT`), item titles, status badges, child accordions, and persistent engine connection footer.
2. **Mode B (Collapsed)**: Fixed width `56px` (`w-14 min-w-[56px]`), showing compact icon rail with 36x36px centered targets, tooltips, active indicator bars, and accessible flyout menus for multi-child modules.
3. Smooth CSS transition (`duration-200 ease-in-out`) between modes.

### Consequences

- Operators on laptops can collapse the sidebar to maximize operational workspace.
- Operators on ultrawide multi-monitor workstations can keep the sidebar fully expanded with all category groups visible.

---

## ADR-0022: Radix Popover Portalling for Accessible Collapsed Rail Flyouts

### Context

When the sidebar is collapsed into a 56px icon rail, modules with child pages (e.g. `Jobs & Applications`, `Agents`, `Settings`) must allow the user to inspect and navigate to child destinations without requiring the user to first re-expand the entire sidebar. Rendering flyouts inside an `overflow-y-auto` sidebar container results in severe CSS clipping and z-index ordering bugs.

### Decision

Implement `SidebarFlyout.tsx` using Radix Popover (`@radix-ui/react-popover`) portalled directly to `document.body`:

1. Use `side="right" align="start" sideOffset={8} avoidCollisions={true}` to dock alongside the rail while auto-adjusting to viewport bounds.
2. Render module header, roadmap stage badge, capability description, and direct links to child routes.
3. Support keyboard `Escape` dismissal and auto-close upon navigation.

### Consequences

- Zero CSS clipping or overflow issues.
- Full keyboard and screen reader accessibility with automatic focus management and backdrop dismiss.

---

## ADR-0023: Zustand LocalStorage Persistence with Transient State Isolation

### Context

Operators customize their navigation view by collapsing specific category groups or collapsing the entire sidebar rail. These layout preferences must persist across application restarts, but transient states such as open modal dialogs or active flyouts must not persist (which would cause confusing floating overlays upon fresh startup).

### Decision

Use Zustand with `persist` middleware configured with custom `partialize`:

1. Persisted durable state: `isExpanded` (boolean), `expandedGroups` (`string[]`), `expandedItems` (`string[]`).
2. Isolated transient state: `activeFlyout` (`string | null`), `isCommandPaletteOpen` (`boolean`).
3. Resilient JSON error handling: corrupted `localStorage` entries fallback safely to sensible defaults without throwing runtime exceptions.

### Consequences

- Instant layout restoration on launch with zero layout flash.
- Zero risk of orphan popups or modal overlays persisting across application restarts.

---

## ADR-0024: Honest Roadmap Module Placeholders and Zero Fabricated Business Data Policy

### Context

In a 50-stage engineering roadmap, certain downstream capabilities (e.g., job scraping, automated application submissions, interview calendars) are scheduled for subsequent stages. Demonstrating complete desktop navigation across all planned routes without implementing the underlying domain logic risks misleading users or introducing fragile fake mocks that pollute testing environments.

### Decision

Enforce the AUTONOM Honest Roadmap Policy:

1. No fabricated business data (no mock jobs, fake recruiter emails, or artificial application submissions).
2. All non-implemented routes resolve to `ModulePlaceholder.tsx`.
3. The placeholder clearly displays the target roadmap stage (e.g., `Stage 26`), category, capability summary, planned sub-capabilities, and quick links back to Command Center or live system diagnostics.

### Consequences

- Clean architectural integrity and transparent progress tracking across all 50 roadmap stages.
- No technical debt from cleaning up fake data generators in future stages.

---

## ADR-0025: Unified Command Center Operational Dashboard Architecture

### Context

AUTONOM is an autonomous multi-agent desktop application where the operator acts as an executive supervisor rather than a manual form-filler. The primary interface must consolidate background execution queues, worker concurrency, recruitment pipelines, system health, and live telemetry without fragmenting into disconnected screens or confusing multi-window interfaces.

### Decision

Implement the Command Center dashboard (`apps/desktop/src/features/dashboard/DashboardView.tsx`) as a 7-tier operational interface:

1. **Dashboard Header**: Real-time service status, loopback HTTP port 8765, uptime counter, dispatch status indicator, and manual sync action.
2. **KPI Metrics Grid**: 4 primary KPI cards (Running, Queued, Jobs Discovered [Stage 26], Applications Submitted [Stage 31]) + 4 secondary supporting metrics (Completed, Failed, Pending Approvals [Stage 14], Worker Threads).
3. **Autonomous Agent Fleet & Worker Pool**: 3 prominent upcoming agent cards (Job Discovery, Application Tailor, Supervisor Swarm) + 1 real Worker Thread Pool card (Stage 03 backend executor).
4. **Recruitment Overview**: Real-time SQLite `job_listings` counts and a 10-stage application pipeline bar (`discovered` through `rejected`).
5. **Live Task Queue & Event Stream**: Interactive task table with state tabs, cooperative cancellation, task inspection dialog, alongside a live SSE event feed.
6. **Analytics, Subsystem Health & Operator Gates**: Recharts task trends over Today, 7 Days, and 30 Days; 4-subsystem health cards; and an actionable failed-tasks review panel.
7. **Quick Operations**: Direct test task dispatcher and one-click navigation shortcuts.

### Consequences

- Operators gain comprehensive, single-screen situational awareness over all autonomous workflows.
- Seamless integration with the Stage 07 expandable/collapsible sidebar without layout disruption.

---

## ADR-0026: Strict Zero-Fake Data & Honest Roadmap Release Attribution Policy

### Context

In an autonomous AI platform, displaying fabricated agent metrics, fake job listings, or artificial application submissions undermines operator trust, compromises debugging accuracy, and introduces technical debt from maintaining dummy data generators.

### Decision

Enforce a strict **Zero-Fake Data Integrity Policy** across the entire Command Center:

1. Real database records: All counts for tasks, jobs, and applications strictly derive from the durable SQLite database (`tasks`, `job_listings`, `applications`).
2. Honest zero state: When no records exist in the database, genuine `0` values are displayed.
3. Explicit roadmap attribution: Capabilities scheduled for future stages explicitly display their release stage badge and explanatory note:
   - Job Discovery Agent: `Roadmap: Stage 26`
   - Application Tailor Agent: `Roadmap: Stage 30`
   - Supervisor Swarm Lead: `Roadmap: Stage 12`
   - Autonomous Submissions: `Roadmap: Stage 31`
   - Advance Permissions Gate: `Roadmap: Stage 14`
4. Distinction between real thread pool (4 active concurrent workers) and future AI agent swarm (Stage 12).

### Consequences

- Absolute truth in telemetry: The operator always knows exactly what code is executing vs what is scheduled.
- Zero leftover mock logic to delete when implementing subsequent stages.

---

## ADR-0027: Hybrid Real-Time Synchronization (SSE Event Stream with Reactive Cache Invalidation)

### Context

Autonomous tasks produce frequent status updates (queued, running, progress, completion, failure). Relying exclusively on high-frequency polling consumes excessive CPU and disk I/O, while relying solely on SSE can lead to desynchronization if events are dropped or client reconnects.

### Decision

Adopt a **Hybrid Real-Time Synchronization Architecture**:

1. **Server-Sent Events (`GET /api/v1/events/stream`)**: Pushes instant lifecycle events directly from the backend `EventBus` to the desktop client.
2. **Client-Side Deduplication**: `useLiveEventStream` maintains a bounded LRU-style set of event IDs (max 500) to prevent duplicate event cards.
3. **Targeted Cache Invalidation**: SSE task transition events immediately invalidate TanStack Query keys (`['dashboard-overview']`, `['dashboard-tasks']`), triggering a focused background fetch.
4. **Reconnection Reconciliation**: When the SSE connection is re-established, all dashboard queries are automatically refetched to synchronize any state accumulated while offline.

### Consequences

- Zero visual latency for task state changes.
- Minimal bandwidth and zero unnecessary CPU spinning.
- 100% state consistency even across network hiccups or application restarts.

---

## ADR-0028: Multi-Window Task Trend Derivation from Durable SQLite State Ledger

### Context

Operators require visibility into recent system productivity and task reliability across multiple time horizons (today, past week, past month). Computing these metrics dynamically on each request without proper indexing could cause database locking in SQLite.

### Decision

Implement optimized multi-window aggregation in `services/api/app/api/v1/endpoints/dashboard.py`:

1. Windows:
   - `today`: 24 hourly buckets (`HH:00`).
   - `7d`: 7 daily buckets (`YYYY-MM-DD`).
   - `30d`: 30 daily buckets (`YYYY-MM-DD`).
2. Queries aggregate SQLite `tasks` filtering on `created_at` with SQLite WAL mode concurrency.
3. Computes derived totals and `overall_success_rate = (completed / (completed + failed)) * 100`.
4. Cached with TanStack Query stale time of 5000ms.

### Consequences

- Instant chart rendering with zero main-thread blocking.
- Reliable historical performance tracking across workstation reboots.

---

## ADR-0029: Multi-Module Workspace Layout and Route Code-Splitting

### Context

AUTONOM is an autonomous multi-agent assistant with 13 core operational modules (Agents, Recruitment, Computer Control, Communications, Interviews, Documents, Coding, Creative, Research, Workflows, Analytics, Activity, Integrations) and over 50 sub-paths. Loading all module bundles synchronously at startup would inflate the initial bundle size and degrade desktop cold-start times.

### Decision

Implement route-level dynamic code-splitting using `React.lazy()` and `Suspense` wrapped around a centralized `<Routes>` architecture in `App.tsx`:

1. Every workspace is authored as a self-contained feature component in `apps/desktop/src/features/<module>/<Module>Workspace.tsx`.
2. Asynchronous chunks are created by Vite Rollup bundler (e.g., `AgentsWorkspace-*.js`, `RecruitmentWorkspace-*.js`).
3. An accessible fallback (`WorkspaceSuspenseFallback`) displays a subtle spinner during chunk streaming.
4. Wildcard child routes (`/agents/*`, `/recruitment/*`) route directly to the parent workspace, which synchronizes active tabs with `location.pathname`.

### Consequences

- Initial bundle size remains compact (<305 kB gzip).
- Each workspace loads on demand when navigated to by the operator.
- Sub-routes and deep links seamlessly render their respective sub-tabs without page reloads.

---

## ADR-0030: Shared Workspace Primitives and State Synchronization

### Context

Without standardized layout primitives, individual workspaces would suffer from inconsistent headers, varied empty states, mismatched loading skeletons, and fragmented toolbar controls.

### Decision

Create a unified shared primitive library in `apps/desktop/src/components/module/`:

- `ModulePage`: Base responsive container with optional right-hand inspector drawer (`ModuleDetailPanel`).
- `ModuleHeader`: Unified title, description, category icon, roadmap stage tag, and header action buttons.
- `ModuleToolbar`: Standardized search input, status/role filter chips, view switcher, and refresh controls.
- `ModuleTabs`: Route-synced tab strip rendering item count badges.
- `ModuleEmptyState`: Honest zero-data fallback message with contextual action buttons.
- `ModuleUnavailableState`: Roadmap stage attribution explaining future autonomous engine activations.
- `ModuleLoadingState`: Responsive skeleton loaders for cards and tables.
- `ModuleErrorState`: Actionable error boundary fallback with connection retry button.
- `ModuleDetailPanel`: Collapsible 384px slide-over inspector for deep-dive object analysis.

### Consequences

- 100% visual and interactive consistency across all 13 modules.
- Fast, accessible keyboard navigation adhering to WCAG 2.1 AA.
- Modular maintainability and simplified unit testing.

---

## ADR-0031: Honest Roadmap Stage Attribution and Zero-Fake-Data UI Pattern

### Context

AUTONOM follows a strict Zero-Fake-Data rule: no synthetic job postings, artificial applications, fake recruiter emails, or fabricated agent performance metrics may be rendered in the production UI. However, modules whose autonomous engines belong to future stages (e.g., Stage 12 Swarm, Stage 16 Browser, Stage 26 Scraper, Stage 31 Application Tailor, Stage 36 Communications, Stage 41 Coding, Stage 42 Docs, Stage 43 Creative, Stage 44 Research, Stage 45 MCP) must still provide a functional UI workspace.

### Decision

Implement the `ModuleUnavailableState` and `ModuleEmptyState` pattern:

1. When genuine data exists (e.g. SQLite job listings, applications, tasks, artifacts), render real data cards with accurate statuses.
2. When autonomous generation engines are scheduled for future roadmap stages, display a prominent `ModuleUnavailableState` banner specifying the exact roadmap stage, scheduled activation purpose, planned capabilities, and architecture readiness.
3. When database tables are legitimately empty, render `ModuleEmptyState` explaining that no records exist yet.

### Consequences

- Absolute truth in telemetry and interface state.
- Zero leftover mock data or synthetic stubs to delete in future stages.
- Users always understand the current operational boundary of the autonomous assistant.

---

## ADR-0032: REST Data Contracts for Jobs, Applications, and Persistent Artifacts

### Context

The Recruitment and Documents workspaces require typed REST API endpoints to read real persistent records stored in the SQLite database (`job_listings`, `applications`, `application_attempts`, and `artifacts`).

### Decision

Add versioned REST endpoints under `/api/v1` in FastAPI:

1. `GET /api/v1/jobs` & `GET /api/v1/jobs/{job_id}`: Paged listings with status and company filtering.
2. `GET /api/v1/applications` & `GET /api/v1/applications/{application_id}`: Paged applications enriched with job metadata and nested execution attempts.
3. `GET /api/v1/artifacts` & `GET /api/v1/artifacts/{artifact_id}`: Paged artifacts with file size, checksum, and retention class.
4. Enforce Bearer token loopback authentication across all endpoints.
5. Create shared TypeScript contracts in `apps/desktop/src/types/modules.ts` and client helper methods in `apps/desktop/src/lib/api-client.ts`.

### Consequences

- Full full-stack integration between React frontend and SQLite database.
- Sub-second local response times with async SQLAlchemy queries.
- Clean separation between durable persistence models and client response schemas.
