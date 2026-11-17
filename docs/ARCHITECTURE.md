# AUTONOM — System Architecture Specification

## 1. Architectural Philosophy & Layered Principles

AUTONOM is architected as an autonomous, production-grade desktop application natively designed for Windows 11. It blends the responsive performance and native operating system integration of **Rust/Tauri** with the rich UI expressiveness of **React 19 / TypeScript / Vite**, the machine learning and asynchronous agent orchestration power of **Python / FastAPI / asyncio**, and the durability of embedded **SQLite**.

### Layered Separation of Concerns (Layers A through F)

AUTONOM strictly enforces unidirectional data flow across six discrete architectural layers to prevent circular dependencies and maintain clear trust boundaries:

```mermaid
flowchart TD
    subgraph LayerA["Layer A — Desktop Presentation (React 19 / Vite / Tailwind)"]
        UI_Dash[Dashboards & Command Center]
        UI_Jobs[Job Queue & Match Explorer]
        UI_Swarm[Agent Swarm Console]
        UI_Settings[Governance & Settings]
    end

    subgraph LayerB["Layer B — Desktop-Native Bridge (Tauri 2 / Rust)"]
        Tauri_IPC[Tauri IPC Dispatcher]
        Tauri_Sup[Child Process Supervisor]
        Tauri_Capture[DXGI Screen Capture Native Bridge]
        Tauri_Hotkeys[Global Hotkeys & Kill Switch]
    end

    subgraph LayerC["Layer C — Backend API (FastAPI / Uvicorn / Asyncio)"]
        API_REST[REST Endpoints /api/*]
        API_WS[WebSocket Streaming /ws/events]
        API_Auth[Authorization Interceptor]
    end

    subgraph LayerD["Layer D — Agent Orchestration (Python Multi-Agent Engine)"]
        Ag_Super[1. Supervisor Agent]
        Ag_Plan[2. Planning Agent]
        Ag_Router[3. Task Router Agent]
        Ag_Verif[4. Verification Agent]
        Ag_Recov[5. Recovery Agent]
        Ag_Swarm[Specialist Agents 6–24]
    end

    subgraph LayerE["Layer E — Tool Execution (Sandboxed Automation Engine)"]
        Tool_Playwright[Playwright Browser Automation]
        Tool_UIA[Windows UI Automation COM Client]
        Tool_SendInput[Windows SendInput Mouse/Keyboard Injection]
        Tool_Workspace[Local Workspace Shell & Git Runner]
        Tool_MCP[Model Context Protocol Client]
    end

    subgraph LayerF["Layer F — Data & Memory (SQLite / WAL / DPAPI Vault)"]
        DB_Relational[SQLite Relational Database (WAL Mode)]
        DB_FTS[SQLite FTS5 Full-Text Search]
        DB_Vault[DPAPI / AES-256-GCM Credential Vault]
        DB_Audit[Immutable Audit & Lineage Log]
    end

    LayerA <-->|Tauri IPC / WebSockets| LayerB
    LayerB <-->|Localhost HTTP / IPC| LayerC
    LayerC <-->|Async Event Loop| LayerD
    LayerD <-->|Validated Tool Dispatch| LayerE
    LayerD <-->|aiosqlite| LayerF
    LayerC <-->|aiosqlite| LayerF
    LayerE -->|State Changes| LayerF
```

---

## 2. Layer Responsibilities & Boundaries

### Layer A — Desktop Presentation

- **Technologies**: React 19, TypeScript (strict), Vite, Tailwind CSS, Lucide icons, Zustand, TanStack Query.
- **Responsibilities**:
  - Information-dense command center and operational dashboards (Stage 08).
  - 13 self-contained operational workspaces with route-level lazy-loading and sub-route synchronization (Stage 09).
  - Centralized Settings & Operational Controls workspace across 15 categories with two-pane layout, dirty-state tracking, and schema validation (Stage 10).
  - Shared workspace primitive architecture (`ModulePage`, `ModuleHeader`, `ModuleToolbar`, `ModuleTabs`, `ModuleDetailPanel`).
  - Collapsible vertical navigation sidebar (expanded 240px and compact 60px icon rail).
  - Real-time agent thought streaming and tool execution cards.
  - Interactive approval modals displaying action diffs for human-in-the-loop governance.
  - Live backend connection health indicator pill in top header.
- **Boundaries**: Strictly UI rendering and local presentation state. Never executes direct OS system calls or raw database queries.

### Layer B — Desktop-Native Bridge

- **Technologies**: Tauri 2.x, Rust 1.80+, Windows Win32 API, `windows-rs`.
- **Responsibilities**:
  - Native window frame controls, system tray icon, and minimize-to-tray behaviors.
  - Subprocess lifecycle management (spawns, monitors, and gracefully halts the Python agent backend).
  - Hardware-accelerated screen frame acquisition (DXGI / Windows Graphics Capture).
  - Global emergency kill-switch hotkey (`Ctrl+Shift+Esc`) hooking.
  - Windows Toast Notifications dispatch to Windows 11 Action Center.
- **Boundaries**: Mediates between WebView2 frontend and the Windows operating system. Exposes typed IPC commands.

### Layer C — Backend API

- **Technologies**: Python 3.11+, FastAPI, Uvicorn, Pydantic v2, `asyncio`.
- **Responsibilities**:
  - Data validation, request parsing, and error schema normalization.
  - REST API routing (`/api/health`, `/api/system`, `/api/agents`, `/api/jobs`, `/api/governance`, `/api/v1/settings`, `/api/v1/integrations`).
  - High-throughput WebSocket server (`/ws/events`) for streaming agent thoughts and telemetry to the UI.
  - Settings management with atomic SQLite WAL serialization, Pydantic v2 validation, and sanitized export/import.
  - Enforcing authorization tiers and permission boundaries before delegating to orchestration.
- **Boundaries**: The network and communication interface for the agent runtime. Bound to `127.0.0.1` only.

### Layer D — Agent Orchestration

- **Technologies**: Python multi-agent execution runtime, asynchronous state machine, dependency DAGs, Specialist Agent Framework (`SpecialistAgent`).
- **Responsibilities**:
  - High-level goal interpretation and plan decomposition (Planning Agent / Supervisor).
  - Dynamic task dispatching and specialist activation (Task Router Agent).
  - 24-Agent Manifest-driven catalog with context isolation and model profile allocation.
  - 32 Granular Specialist Capabilities spanning recruitment, computer operations, coding, research, productivity, creative design, messaging, and automation.
  - Post-action verification and schema assertion (Verification Agent).
  - Self-reflection, retry management, and replanning (Recovery Agent).
  - Single-active-model semaphore hardware protection for NVIDIA RTX 4050 6GB Laptop GPU.
- **Boundaries**: Pure reasoning and orchestration logic. Interacts with the real world exclusively through Layer E (Tools) and Layer F (Data). Enforces context isolation so specialist agents cannot access raw credentials.

### Layer E — Tool Execution

- **Technologies**: Playwright, Windows UI Automation (COM), Windows `SendInput`, Subprocess Runner, MCP Client.
- **Responsibilities**:
  - Browser automation: Headless/headed navigation, form filling, document uploads.
  - Structural UI interaction: Traversal of Windows accessibility trees and programmatic pattern invocation.
  - Visual UI interaction: Mouse trajectory generation, keystroke simulation, coordinate grounding.
  - Local workspace automation: Sandboxed shell execution, git operations, file parsing.
  - Model Context Protocol (MCP) integrations: Connecting to external tools and data resources.
- **Boundaries**: Encapsulates all real-world side effects. Enforces timeout limits, sandboxing, and execution safety masks.

### Layer F — Data and Memory

- **Technologies**: SQLite 3, `aiosqlite`, FTS5, Windows Data Protection API (DPAPI), AES-256-GCM.
- **Responsibilities**:
  - Persistent application state (ApplicantProfile, VerifiedSkill, JobListing, Application, AppSettings).
  - Full-text search over job listings and resume texts using SQLite FTS5.
  - Machine-bound cryptographic secret storage for credentials, OAuth tokens, and API keys.
  - Durable task execution queues, checkpoints, and immutable audit logs.
  - Atomic settings persistence across 13 categories under `settings:<category>`.
- **Boundaries**: The single source of durable truth for AUTONOM. Independent of external database servers.

---

## 3. System Process Topology

```
+-----------------------------------------------------------------------------------+
|                               Windows 11 Workstation                              |
|                                                                                   |
|  +-----------------------------------------------------------------------------+  |
|  |                           Tauri Desktop Process (Rust)                      |  |
|  |  - Native Windows Windowing & System Tray                                   |  |
|  |  - Process Supervisor (Spawns & Monitors Python Backend)                    |  |
|  |  - Windows DPAPI Native Cryptography Bridge                                 |  |
|  |  - High-Speed Screen Capture & Global Hotkeys                               |  |
|  |                                                                             |  |
|  |  +-----------------------------------------------------------------------+  |  |
|  |  |                 WebView2 UI Layer (React 19 + TypeScript)             |  |  |
|  |  |  - Dark Dashboard (Restrained Blue/Cyan Accents)                       |  |  |
|  |  |  - Collapsible Sidebar Navigation (Expanded & Compact Icon-Only)       |  |  |
|  |  |  - Real Interactive Control Panels & Telemetry Streams                 |  |  |
|  |  |  - Live Health Pill Indicator & Real Backend Querying                 |  |  |
|  |  +-----------------------------------+-----------------------------------+  |  |
|  +--------------------------------------|---------------------------------------+  |
|                                         | IPC (HTTP REST & WebSockets)             |
|                                         v                                          |
|  +-----------------------------------------------------------------------------+  |
|  |                    Agent Backend Process (Python 3.11+ / FastAPI)           |  |
|  |                                                                             |  |
|  |  +---------------------+  +---------------------+  +---------------------+  |  |
|  |  |   Agent Engine      |  | Dual Interaction    |  | Job & Career Hub    |  |  |
|  |  |  - Multi-LLM Gateway|  |  - Visual Grounding  |  |  - Discovery Scraper|  |  |
|  |  |  - Plan-Exec-Verify |  |  - Windows UIA COM   |  |  - AST Resume Parser|  |  |
|  |  |  - Swarm Board      |  |  - Playwright Engine |  |  - Factual Tailorer |  |  |
|  |  |  - Dynamic Sandbox  |  |  - Safe Guardrails   |  |  - Auto-Submitter   |  |  |
|  |  +----------+----------+  +----------+----------+  +----------+----------+  |  |
|  |             |                        |                        |             |  |
|  |             +------------------------+------------------------+             |  |
|  |                                      |                                      |  |
|  |  +-----------------------------------+-----------------------------------+  |  |
|  |  |                Core Persistence & Security Layer                      |  |  |
|  |  |  - SQLite Async Engine (WAL mode, Foreign Keys, Pragma optimizations)  |  |  |
|  |  |  - DPAPI / AES-256-GCM Secure Key Vault                               |  |  |
|  |  |  - Immutable Event & Audit Logger                                     |  |  |
|  |  +---------------------------------------+-------------------------------+  |  |
|  +-----------------------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## 4. Error Handling & Recovery Model

AUTONOM employs an autonomous supervision tree:

1. **Tool-Level Failures**: Transient exceptions (e.g., HTTP 429, element momentarily detached) are handled locally by retry decorators with exponential backoff.
2. **Step-Level Failures**: If a step fails post-action verification, the Verification Agent halts the branch and activates the **Recovery Agent**. The Recovery Agent consults past failure memory, clears corrupted session cookies, or attempts an alternative interaction modality (e.g., falling back from structural UIA to visual grounding).
3. **Subprocess-Level Failures**: If the Python backend process terminates unexpectedly, the Tauri child process supervisor detects the loss of heartbeat, captures exit telemetry, relaunches the Python backend within 2 seconds, and restores in-flight tasks from the durable SQLite state checkpoint.

---

## 5. Command Center Supervision Architecture (Stage 08)

The Stage 08 Command Center implements an executive supervision layer connecting the operator directly to the underlying autonomous systems:

1. **Reactive Telemetry Bridge**: Server-Sent Events (`/api/v1/events/stream`) push lifecycle updates from the backend `EventBus` to the desktop client.
2. **Client-Side Deduplication & Query Cache Reconciliation**: `useLiveEventStream` maintains an LRU-style set of event IDs to eliminate duplicate messages, triggering selective invalidation of TanStack Query keys (`['dashboard-overview']`, `['dashboard-tasks']`) for instantaneous updates without polling loops.
3. **Data Integrity & Zero-Fake Data Enforcement**: Real counts derive from SQLite tables (`tasks`, `job_listings`, `applications`). Capabilities awaiting subsequent roadmap stages (Stage 12 Swarm, Stage 14 Approvals, Stage 26 Job Discovery, Stage 30 Resume Tailoring, Stage 31 Submissions) are strictly rendered with honest zeros and roadmap attribution badges.
4. **Cooperative Task Control**: The Command Center enables direct cooperative task cancellation, parameter inspection, and state transition ledger examination without terminating worker threads.
