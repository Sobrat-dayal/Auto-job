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
