# AUTONOM — 50-Stage Master Development Roadmap

AUTONOM is an enterprise-grade, production-oriented, multi-agent Windows 11 desktop application designed for autonomous job discovery, resume tailoring, application submission, email handling, interview preparation, dual-mode computer interaction (visual and structural), and extensible workspace automation.

---

## Roadmap Overview

| Phase                                                               | Stages       | Focus Area                                                                                                                                                                                                                                                   |
| :------------------------------------------------------------------ | :----------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Phase 1: Foundations & Desktop Shell**                            | Stages 01–10 | Architecture, Tauri desktop harness, React UI shell, Python FastAPI backend, SQLite, DPAPI secure vault, process lifecycle, event bus, autonomy governance, and crash resilience.                                                                            |
| **Phase 2: Agent Orchestration & Intelligence Runtime**             | Stages 11–20 | Multi-provider LLM gateway, plan-execute-verify-recover agent runtime, episodic/semantic memory, multi-agent swarm arbitration, tool execution sandbox, MCP client, and replay debugging.                                                                    |
| **Phase 3: Dual Computer Interaction**                              | Stages 21–30 | High-performance screenshot capture, visual grounding (OCR/coordinates), native Windows input injection, Windows UI Automation (UIA) tree traversal, Playwright browser engine, hybrid interaction arbiter, and safe interaction guardrails.                 |
| **Phase 4: Autonomous Job Search & Career Operations**              | Stages 31–40 | Factual career profile store, multi-format resume parsing, multi-board scraping (LinkedIn, Indeed, Greenhouse, Lever, Workday), semantic match scoring, ATS resume tailoring, automated application submission, email tracking, and interview prep dossiers. |
| **Phase 5: Extended Workspace Tools, Media & Production Hardening** | Stages 41–50 | Code automation runner, autonomous research compiler, Office/document generators (DOCX/PDF/PPTX/XLSX), 3D & media pipelines, communication webhooks, stress testing, performance profiling, and Windows MSIX/NSIS release packaging.                         |

---

## Detailed Stage Breakdown

### Phase 1: Core Foundation & Desktop Shell Architecture (Stages 01–10)

#### Stage 01: Project Foundation, Core Monorepo Scaffold, Backend Core & Tauri App Foundation

- **Goal**: Establish the complete AUTONOM repository structure, core architectural documentation, desktop Tauri/React/TypeScript scaffold, Python FastAPI backend service, and end-to-end integration test harness.
- **Key Deliverables**:
  - Monorepo structure (`apps/desktop`, `services/agent_backend`, `packages/shared`, `docs`, `tests`).
  - Architecture, security, API contracts, ADRs, and stage progression logs.
  - Python FastAPI service with health, telemetry, and agent status endpoints.
  - React/TypeScript desktop dashboard shell with dark theme and live backend health heartbeat.
  - Automated tests verifying API contracts, backend health, database readiness, and frontend build.
- **Acceptance Criteria**: Backend launches cleanly, SQLite database connects with WAL mode, desktop UI loads with live backend connection status pill, and test suite passes 100%.

#### Stage 02: Design System & Desktop Dashboard Shell

- **Goal**: Implement the dark AUTONOM dashboard design system with restrained blue/cyan accents, collapsible sidebar with icon-only mode, information-dense layout, and real interactive controls.
- **Key Deliverables**:
  - Tailwind CSS / CSS variable theme tokens (dark background `#090d16`, borders `#1e293b`, accents `#2563eb`/`#06b6d4`).
  - Collapsible navigation sidebar (Dashboard, Jobs, Swarm, Computer Use, Workflows, Settings).
  - Metric summary cards, interactive filter toolbars, activity stream, and system status indicators.
- **Acceptance Criteria**: UI matches design specifications, responsive navigation with icon-only collapsed mode, zero decorative dead buttons, zero purple gradients.

#### Stage 03: Process Lifecycle & Inter-Process Communication (IPC) Bridge

- **Goal**: Build a bidirectional, resilient IPC bridge between Tauri (Rust) and the Python FastAPI backend with managed child process spawning and graceful termination.
- **Key Deliverables**:
  - Rust process supervisor managing Python backend lifecycle.
  - IPC command handlers for frontend-to-native-to-backend requests.
  - Heartbeat watchdog detecting backend hung states and triggering auto-restart.
- **Acceptance Criteria**: Desktop app starts Python backend automatically, gracefully terminates on app exit without orphaned processes, and handles backend restart transparently.

#### Stage 04: SQLite Database Engine, Migrations & Schema Architecture (Completed)

- **Status**: COMPLETE (2026-11-16)
- **Goal**: Implement local relational persistence using SQLite with Write-Ahead Logging (WAL), foreign key enforcement, connection pooling, automated schema migrations, Windows DPAPI/AES-256-GCM secure storage, online consistent backups, verified restoration, and persistent task state reconciliation.
- **Key Deliverables**:
  - Asynchronous database engine (`aiosqlite` + SQLAlchemy 2.x) with WAL mode, foreign keys, and 10s busy timeout.
  - Relational schema across 17 tables (settings, profiles, skills, evidence, resumes, job sources, listings, matches, applications, attempts, tasks, events, workers, agents, artifacts, credentials, audit).
  - Alembic migrations runner with `001_initial_schema.py` and programmatic runner.
  - Windows DPAPI and AES-256-GCM cryptographic vault for field-level contact encryption and credential protection.
  - Repository layer with typed CRUD, deduplication, and encryption wrappers.
  - Persistent task execution manager with startup crash reconciliation and durable event history.
  - Consistent online backup (`sqlite3.backup`) with SHA-256 manifests, pre-restore safety snapshots, and verified restoration.
  - Storage diagnostics UI in desktop React frontend (`Storage.tsx`) and 6 PowerShell database automation scripts.
- **Acceptance Criteria**: All 25 live verification gates passed, concurrent WAL writes succeed without lockouts, contact info and secrets encrypted at rest without plaintext leakage, state restored cleanly from verified backups, 43 unit/integration tests passing.

#### Stage 05: Windows Desktop Shell, Native Integration, Backend Sidecar, Process Supervision, Crash Recovery, and Application Lifecycle (Completed)

- **Status**: COMPLETE (2026-11-16)
- **Goal**: Transform AUTONOM into a real, self-contained Windows desktop application that manages its own local services, supervises the Python backend sidecar, recovers from crashes, and operates reliably without requiring external terminals.
- **Key Deliverables**:
  - Tauri 2 desktop harness with single-instance enforcement, system tray context menus, and native notifications.
  - Kernel-enforced process containment using Win32 Job Object with `JOB_OBJECT_LIMIT_KILL_ON_JOB_CLOSE`.
  - Packaged Python backend sidecar via PyInstaller (`autonom-api-x86_64-pc-windows-msvc.exe`) with loopback isolation (`127.0.0.1`) and bearer token bootstrap.
  - Supervisor state machine (`Stopped`, `Starting`, `Connecting`, `Ready`, `Degraded`, `Restarting`, `Failed`, `Stopping`) with bounded exponential backoff crash recovery.
  - Multi-monitor safe window state persistence (`%LOCALAPPDATA%\AUTONOM\config\desktop_settings.json`).
  - Desktop Diagnostics UI dashboard (`DesktopDiagnostics.tsx`) with supervisor controls and folder shortcuts.
  - Automated packaging and verification pipeline (`package-backend.ps1`, `package-desktop.ps1`, `verify-package.ps1`, `verify_stage05_live.py`).
- **Acceptance Criteria**: Desktop executable launches and starts backend automatically, readiness confirmed on `/api/v1/ready`, single-instance brings window to focus, abnormal process kill triggers bounded restart with task reconciliation, all 20 live verification gates pass.

#### Stage 06: Complete UI/UX Design System, React Component Library, Design Tokens, Accessibility, and Desktop Layout Foundations (Completed)

- **Status**: COMPLETE (2026-11-16)
- **Goal**: Implement Phase 2 frontend design foundations, centralized design tokens, disciplined dark Windows dashboard aesthetic, full React component library (`@radix-ui/react-*` + CVA + Tailwind), responsive desktop layout primitives, operational data displays, dark charts, dynamic density modes (`comfortable` vs `compact`), WCAG 2.2 AA accessibility, and interactive component showcase.
- **Key Deliverables**:
  - Centralized design token system (`tokens.css`, `typography.css`, `tailwind.config.js`).
  - Dark Windows 11 high-density dashboard palette (`#0B1220`, `#0F1828`, `#121E30`, `#1B2B42`, `#338BDF`, `#51C8E8`).
  - Accessible React component library: Button, Input, Textarea, Checkbox, Switch, Select, Badge, Progress, Skeleton, Separator, Tooltip, Dialog, DropdownMenu, Tabs.
  - Desktop layout primitives: `PageContainer`, `SectionHeader`, `SplitPanel`.
  - Structured operational displays: `MetricCard`, `StatusCard`, `EmptyState`, `DataTable` (TanStack Table v8).
  - Dark analytics charts: `LineChart`, `BarChart`, `DonutChart` (Recharts).
  - Feedback primitives: `ErrorState`, `LoadingState`, `Toast` + `useToast()`.
  - Dynamic density modes (`comfortable` vs `compact`) with `ThemeContext` and `localStorage` persistence.
  - Interactive Design System showcase (`DesignSystemShowcase.tsx`) with 20 aspect fixtures.
  - Complete migration of all existing screens (`Overview`, `Diagnostics`, `Storage`, `DesktopDiagnostics`, `Header`, `Sidebar`).
- **Acceptance Criteria**: All 9 test files / 30 tests pass, clean TypeScript compilation, WCAG 2.2 AA contrast and keyboard accessibility verified, zero breaking changes to existing backend sidecar, SSE, or storage workflows.

#### Stage 07: Advanced Expandable and Collapsible Sidebar, Navigation Architecture, Nested Menus, Flyouts, Keyboard Shortcuts, and Persistent UI State (Completed)

- **Status**: COMPLETE (2026-11-16)
- **Goal**: Implement the complete Windows desktop navigation architecture using a dual-mode expandable and collapsible sidebar, typed routing across 16 top-level modules and 50+ child sub-routes, accessible portalled flyout menus for collapsed icon-rail mode, hierarchical breadcrumbs, modal Command Palette (`Ctrl+K`), global keyboard shortcuts (`Ctrl+B`), durable Zustand state persistence, and honest roadmap module placeholders with zero fabricated business data.
- **Key Deliverables**:
  - Typed navigation contracts: `apps/desktop/src/config/navigation-types.ts` (`NavigationGroup`, `NavigationItem`, `NavigationChildItem`, `BreadcrumbItem`, `NavigationAvailability`).
  - Comprehensive navigation registry: `apps/desktop/src/config/navigation.ts` covering 5 functional groups (`MAIN`, `RECRUITMENT`, `WORKSPACE`, `MANAGEMENT`, `DEVELOPMENT`), 16 top-level modules, and 50+ sub-routes with roadmap stage attribution.
  - Persistent sidebar state store: `apps/desktop/src/stores/sidebarStore.ts` with Zustand `persist` middleware, localStorage persistence (`autonom_sidebar_state`), and transient state isolation (`activeFlyout`, `isCommandPaletteOpen`).
  - Dual-mode sidebar implementation: `AppSidebar.tsx` switching between 240px expanded mode (`w-60`) and 56px collapsed rail (`w-14`) with smooth CSS transitions.
  - Header & footer regions: `SidebarHeader.tsx` (brand, logo, collapse button), `SidebarFooter.tsx` (real FastAPI backend status dot, port 8765, settings shortcut, uptime counter).
  - Nested menus & disclosures: Accordion sub-menus with chevron indicators, active route highlighting, and active parent indicators.
  - Portalled flyout menus: `SidebarFlyout.tsx` leveraging Radix Popover portalled to `document.body` for zero clipping in collapsed rail mode, with keyboard Escape dismissal.
  - Breadcrumbs component: `NavigationBreadcrumbs.tsx` automatically deriving route hierarchy via `getBreadcrumbsForPath()`.
  - Global Command Palette: `CommandPalette.tsx` accessible via `Ctrl+K` with real-time search filtering, arrow key navigation, and instant Enter route selection.
  - Honest roadmap placeholder: `ModulePlaceholder.tsx` surfacing target roadmap stages and planned capabilities without fabricating business mock data.
  - Desktop routing refactoring: `App.tsx` wrapped in `HashRouter` with route protection and integration across existing screens and placeholders.
  - Complete navigation test suite: 4 new test files covering sidebar rendering, flyouts, keyboard shortcuts, and state persistence (46 total desktop tests passing).
- **Acceptance Criteria**: 100% test pass rate (13 test files / 46 tests), zero TypeScript compilation errors, smooth mode toggling, persistent user preferences, full WCAG 2.2 AA keyboard accessibility, and production build succeeded.

#### Stage 08: Complete Command Center Dashboard, Real-Time Agent Monitoring, Job Pipeline Visualization, Task Management, Live Activity, and Operational Analytics

- **Status**: Complete (Stage 08)
- **Goal**: Build the real, integrated full-stack operational dashboard for AUTONOM to supervise autonomous agents, background task queues, recruitment pipelines, system health, and live telemetry.
- **Key Deliverables**:
  - Backend Telemetry Endpoints (`services/api/app/api/v1/endpoints/dashboard.py`):
    - `GET /api/v1/dashboard/overview`: Consolidated telemetry, task state counts, SQLite job & application pipeline counts, agent operation states, worker capacity, and pending action items.
    - `GET /api/v1/dashboard/task-trends`: Multi-window task execution aggregation (`today`, `7d`, `30d`) with overall success rates.
    - `GET /api/v1/dashboard/activity`: Durable task transition events from SQLite `task_events`.
    - `GET /api/v1/tasks/{task_id}/history`: SQLite state transition audit ledger for inspect modal.
  - Frontend Typed Contracts & Client (`apps/desktop/src/types/dashboard.ts`, `apps/desktop/src/lib/api-client.ts`).
  - React Query Hooks & SSE Stream (`apps/desktop/src/hooks/use-dashboard.ts`): Bounded client-side deduplication (500 event IDs), automatic cache invalidation, and reconnection recovery.
  - 13 Dashboard Components (`apps/desktop/src/features/dashboard/`):
    - `DashboardView`: Comprehensive 7-tier operational supervisor grid.
    - `DashboardHeader`: Loopback HTTP 8765 badge, uptime counter, global dispatch pill, Stage 08 release tag.
    - `DashboardKpiGrid`: 4 primary KPI cards + 4 secondary supporting metrics with filter navigation.
    - `AgentOperationsPanel`: 3 prominent swarm agent status cards (Stage 26, Stage 30, Stage 12) + 1 real Worker Thread Pool card (Stage 03 Active).
    - `JobDiscoveryOverview`: Real-time SQLite `job_listings` counts and Stage 26 scraper notice.
    - `ApplicationPipeline`: 10-stage application lifecycle bar and Stage 31 automated submissions notice.
    - `LiveTaskQueue`: Filter tabs, progress bars, inspect dialog trigger, cooperative cancellation.
    - `TaskDetailModal`: Accessible Radix Dialog showing UUID, durations, error details, output JSON, state history ledger.
    - `ActivityFeed`: Live SSE activity feed with category filters, memory bounds, stream health pill.
    - `ProductivityChart`: Recharts dark theme task trends over Today, 7 Days, 30 Days.
    - `SystemHealthPanel`: Subsystem breakdown (Backend API, Worker Manager, SQLite WAL, Tauri Desktop).
    - `PendingActionsPanel`: Actionable failed task reviews and Stage 14 authorization notice.
    - `QuickActions`: Direct test task dispatcher and one-click navigation shortcuts.
  - Integration into `Overview.tsx` and desktop routing.
  - Automated Test Suites:
    - 5 frontend dashboard test suites in `apps/desktop/src/test/dashboard/` (19 tests).
    - Full desktop test suite passed: 18 test files, 65 tests passing.
    - Backend dashboard integration tests passed: 47 pytest tests passing.
- **Acceptance Criteria**: 100% test pass rate, zero TypeScript errors (`tsc && vite build`), strict zero-fake data integrity, honest roadmap release attribution, and full desktop integration.

#### Stage 09: Complete Application Module Screens, Workspace Architecture, Route Integration, Functional Page Foundations, and Cross-Module Navigation [COMPLETED]

- **Goal**: Transform the AUTONOM desktop UI into a multi-module workspace covering all 13 core modules + settings with lazy loading, sub-route synchronization, shared layout primitives, and Zero-Fake-Data compliance.
- **Key Deliverables**:
  - 13 self-contained feature workspaces in `apps/desktop/src/features/`:
    - `AgentsWorkspace` (`/agents/*`): 24-agent catalog across 4 tiers, active worker capacity, live task query, slide-over agent inspector.
    - `RecruitmentWorkspace` (`/recruitment/*`): SQLite job listings, 10-stage pipeline, submission attempts, job/app inspector.
    - `ComputerWorkspace` (`/computer/*`): Dual-modality perception (Visual Grounding + Windows UIA), safety boundaries, hardware killswitch.
    - `CommunicationsWorkspace` (`/communications/*`): Unified recruiter correspondence inbox, channel tabs, draft staging view.
    - `InterviewsWorkspace` (`/interviews/*`): Interview calendar view, STAR prep dossiers, conversational mock interview studio shell.
    - `DocumentsWorkspace` (`/documents/*`): SQLite artifact metadata, file size formatting, SHA-256 checksums, retention classes.
    - `CodingWorkspace` (`/coding/*`): Repository manager, build/test runs, AST code edits, diff review shell.
    - `CreativeWorkspace` (`/creative/*`): Three.js WebGL canvas shell, Blender render queue, animation timelines.
    - `ResearchWorkspace` (`/research/*`): Market intelligence queries, company profile dossiers, salary benchmark briefs.
    - `WorkflowsWorkspace` (`/workflows/*`): Persistent task execution, diagnostic task dispatch, cooperative cancellation, DAG builder canvas shell.
    - `AnalyticsWorkspace` (`/analytics/*`): Real-time Recharts charts, task volumes, duration averages, success ratios, multi-window filters.
    - `ActivityWorkspace` (`/activity/*`): Immutable SQLite event ledger, state transition tracking, JSON payload inspector.
    - `IntegrationsWorkspace` (`/integrations/*`): External AI model providers, MCP tool servers, ATS platforms, DPAPI vault keys.
  - Shared Workspace Primitives (`apps/desktop/src/components/module/`):
    - `ModulePage`, `ModuleHeader`, `ModuleToolbar`, `ModuleTabs`, `ModuleEmptyState`, `ModuleUnavailableState`, `ModuleLoadingState`, `ModuleErrorState`, `ModuleDetailPanel`.
  - Router & Code-Splitting:
    - Route-level lazy loading (`React.lazy()` + `Suspense`) in `App.tsx` producing 13 distinct code-split chunks.
    - URL sub-path synchronization supporting direct deep-links and browser history.
  - Backend REST API Endpoints:
    - `GET /api/v1/jobs` & `GET /api/v1/jobs/{job_id}`
    - `GET /api/v1/applications` & `GET /api/v1/applications/{application_id}`
    - `GET /api/v1/artifacts` & `GET /api/v1/artifacts/{artifact_id}`
  - Automated Verification:
    - 26 frontend Vitest test files passing (90 tests passing, 100% pass rate).
    - 57 backend Pytest integration tests passing (100% pass rate).
    - Zero TypeScript errors (`tsc --noEmit` and `vite build` clean exit 0).
- **Acceptance Criteria**: All 13 modules accessible, Zero-Fake-Data compliance strictly enforced, honest roadmap stage attribution, sub-routes synchronized, and full production build passing.

#### Stage 10: Advanced Settings, Integration Configuration, Security Controls, Agent Preferences, Windows Operations, and Unified Application Management [COMPLETED]

- **Status**: COMPLETE (Stage 10 of 50 — 2026-11-17)
- **Goal**: Implement the centralized, strongly-typed settings and operational control plane for AUTONOM across 15 categories, connecting frontend controls to real backend Pydantic models, SQLite WAL persistence, Windows DPAPI vault references, and native desktop capabilities with Zero-Fake-Data compliance.
- **Key Deliverables**:
  - **Backend Settings Architecture & REST Endpoints** (`services/api/app/schemas/settings.py`, `services/api/app/repositories/settings_repository.py`, `services/api/app/api/v1/endpoints/settings.py`):
    - 13 comprehensive Pydantic v2 schemas: General, Appearance, AI, Agents, Automation, Permissions, Computer Control, Integrations, Recruitment, Storage, Notifications, Desktop, Security & Privacy.
    - Full REST CRUD API: `GET /settings/all`, `GET /settings/{cat}`, `PATCH /settings/{cat}`, `POST /settings/{cat}/reset`, `POST /settings/reset`, `GET /settings/schema`, `GET /settings/export`, `POST /settings/import`.
    - Integration configurations endpoint: `GET /api/v1/integrations/configurations`.
    - 9 backend pytest integration tests in `test_api_settings.py` (66 total backend tests passing, 100% pass rate).
  - **Shared TypeScript Type Contracts** (`packages/shared-types/src/settings.ts`, `packages/shared-types/src/index.ts`):
    - Strongly typed interfaces mirroring backend Pydantic models 1:1.
    - Verified with `pnpm --filter @autonom/shared-types typecheck`.
  - **Frontend Client & Navigation Integration** (`apps/desktop/src/lib/api-client.ts`, `apps/desktop/src/config/navigation.ts`, `apps/desktop/src/App.tsx`):
    - Complete API client methods for settings operations, credential vaulting, and export/import.
    - Updated navigation registry with all 15 settings sub-routes marked as `implemented`.
    - Route-level lazy loading (`React.lazy()`) for `SettingsWorkspace` in `App.tsx`.
  - **Settings Shared Primitives & 15 Category Pages** (`apps/desktop/src/features/settings/`):
    - Primitives: `SettingsLayout`, `SettingsNavigation`, `SettingsSection`, `SettingsField`, `SettingsToggle`, `SettingsSaveBar`, `SettingsRestartNotice`, `SettingsUnavailableState`, `SettingsConfirmationDialog`.
    - 15 Category Pages:
      1. `GeneralSettingsPage.tsx` (`/settings/general`)
      2. `AppearanceSettingsPage.tsx` (`/settings/appearance`)
      3. `AIProviderSettingsPage.tsx` (`/settings/ai` — RTX 4050 6GB VRAM bounds, single active model)
      4. `AgentPreferencesPage.tsx` (`/settings/agents` — 24 agent profiles, approval tiers)
      5. `AutomationSettingsPage.tsx` (`/settings/automation` — worker concurrency 1-8, queue depth, timeouts)
      6. `PermissionSettingsPage.tsx` (`/settings/permissions` — 14-category action matrix, `Pause` hotkey)
      7. `ComputerControlSettingsPage.tsx` (`/settings/computer` — structural vs visual, process boundaries)
      8. `IntegrationSettingsPage.tsx` (`/settings/integrations` — MCP tool servers, DPAPI status)
      9. `RecruitmentSettingsPage.tsx` (`/settings/recruitment` — ATS thresholds, salary, quotas)
      10. `StorageSettingsPage.tsx` (`/settings/storage` — live SQLite stats, backup snapshots, restore)
      11. `NotificationSettingsPage.tsx` (`/settings/notifications` — toast routing, test notification action)
      12. `DesktopSettingsPage.tsx` (`/settings/desktop` — Windows startup, tray, backend restart action)
      13. `SecuritySettingsPage.tsx` (`/settings/security` — DPAPI vault health, store secret modal, revoke)
      14. `DiagnosticsSettingsPage.tsx` (`/settings/diagnostics` — live process probes, export bundle)
      15. `AboutSettingsPage.tsx` (`/settings/about` — app/backend/Tauri versions, update attribution)
  - **Automated Verification**:
    - 14 new frontend Vitest tests across 3 files (`settings-workspace.test.tsx`, `settings-categories.test.tsx`, `settings-export-import.test.tsx`).
    - Full desktop test suite passed: **29 test files, 104 tests passing (100% pass rate in 20.35s)**.
    - Full backend test suite passed: **66 pytest tests passing in 5.51s**.
    - Rust native suite passed: **6 tests passing, clippy clean**.
    - Production Vite build passed (Settings chunk: 106.41 kB).
- **Acceptance Criteria**: 100% test pass rate across all 3 suites, strict Zero-Fake-Data compliance, truthful roadmap attribution, DPAPI credential safety, and persistent SQLite WAL configuration. Phase 2 (Frontend & User Experience) officially concluded. Ready for Stage 11 (Unified AI Model Gateway).

---

### Phase 2: Agent Orchestration Engine & Local/Cloud Intelligence Runtime (Stages 11–20)

#### Stage 11: Unified AI Model Gateway, Local/Cloud Inference, Routing, Streaming, and Hardware Optimization (Completed)

- **Status**: COMPLETE (2026-11-17)
- **Goal**: Implement a production-grade, unified AI Model Gateway supporting local Ollama (`127.0.0.1:11434`), cloud OpenAI, and OpenAI-compatible providers, with RTX 4050 6GB single-active-model memory guardrails, NVML telemetry, 16-category intelligent model routing, real-time SSE token streaming, token accounting, and complete desktop UI workspace (AI Playground, Model Management, Model Routing, and AI Usage Analytics).
- **Key Deliverables**:
  - `AIGateway` facade and provider adapters (`OllamaProvider`, `OpenAIProvider`, `OpenAICompatibleProvider`).
  - `LocalModelResourceController` with direct NVML C-bindings (`nvidia-ml-py`) enforcing single active model in VRAM and 5.0 GB memory cap.
  - `IntelligentModelRouter` supporting 16 specialization categories, 7 routing strategies, category preferences, and explainable decision trees.
  - Real-time Server-Sent Events (SSE) token streaming via `/api/v1/ai/chat/stream` with cooperative client cancellation.
  - `ContextBudgetManager` with `tiktoken` (cl100k_base) and `TokenBudgetManager` with exact pricing calculations.
  - SQLite persistence across 3 new tables: `ai_models`, `ai_requests`, `ai_routing_preferences`.
  - Full desktop frontend workspace (`/ai/*`): AI Playground, Model Management, Model Routing, Hardware Telemetry, and AI Usage Analytics.
  - Zero-Fake-Data compliance: honest discovery reporting, no simulated models, no unprompted large downloads.
  - 10 automated backend pytest tests and 5 automated frontend Vitest tests (100% pass rate).
- **Acceptance Criteria**: Verified local and cloud inference execution, dynamic model switching without GPU OOM crashes, streaming token delivery, and complete documentation. Ready for Stage 12 (Base Agent Runtime & PEVR Architecture).

#### Stage 12: Base Agent Runtime & Plan-Execute-Verify-Recover Architecture [COMPLETE]

- **Goal**: Core multi-agent orchestration runtime implementing structured reasoning, dynamic planning, dependency graphs, capability dispatching, multi-layer verification, and 13-category error recovery.
- **Key Deliverables**:
  - 5 Core Logical Agents: Supervisor Agent (`supervisor`), Planning Agent (`planner`), Task Router Agent (`router`), Verification Agent (`verifier`), Recovery Agent (`recovery`), plus Safe Capability Worker (`capability_worker`).
  - 8 Relational database tables: `workflows`, `workflow_plans`, `workflow_steps`, `workflow_dependencies`, `agent_executions`, `agent_messages`, `verification_results`, `recovery_attempts`.
  - DAG Engine: Kahn's algorithm cycle detection, topological sorting, multi-level parallel stages, and mustache input binding resolution (`{{step_x.field}}`).
  - 7 Safe Capabilities: `text_summarize`, `text_classify`, `structured_extract`, `text_compare`, `data_transform`, `output_validate`, `code_inspect`.
  - Hardware Guardrail: Single-active local LLM slot semaphore for NVIDIA GeForce RTX 4050 6GB Laptop GPU.
  - End-to-end recruitment workflow: Analyzes job description, extracts technical skills, summarizes responsibilities, classifies domain, and compiles structured markdown report.
  - Desktop UI: Workflows Workspace (`/workflows`) with natural language goal builder, interactive DAG visualizer, step inspector drawer, and pause/resume/cancel controls; Agents Workspace (`/agents`) with real Stage 12 coordination agent statuses.
  - 10 new architectural documents (`MULTI_AGENT_ARCHITECTURE.md`, `SUPERVISOR_AGENT.md`, `PLANNING_ENGINE.md`, `AGENT_ROUTING.md`, `WORKFLOW_DAG.md`, `AGENT_COMMUNICATION.md`, `AGENT_VERIFICATION.md`, `AGENT_RECOVERY.md`, `ORCHESTRATION_SECURITY.md`, `ORCHESTRATION_TESTING.md`) and ADR-0041 to ADR-0044.
- **Acceptance Criteria**: 84/84 Pytest unit & integration tests passed; 110/110 Vitest frontend tests passed; end-to-end recruitment workflow executed successfully. Ready for Stage 13. DO NOT begin Stage 13 until explicitly instructed.

#### Stage 13: Specialist AI Agent Framework, Agent Registry, Recruitment Agents, Computer Agents, Coding Agents, Research Agents, Productivity Agents, Communication Agents, Creative Agents, and Multi-Agent Collaboration [COMPLETE]

- **Goal**: Full specialist AI agent framework and typed agent registry integrating all 24 planned agent roles into the multi-agent runtime, with strict context isolation, model profiling, execution timeouts, honest capability attribution, and multi-agent collaboration workflows.
- **Key Deliverables**:
  - Specialist Agent Base Framework (`SpecialistAgent`) with lifecycle management, input/output validation, context isolation (credential rejection), execution cancellation, and capability dispatching.
  - Complete 24-Agent Catalog defined via strongly typed `AgentManifest` schemas: 5 Core Orchestration Agents, 1 Safe Capability Worker, 6 Recruitment Specialists, 4 Computer Control Specialists, 1 Coding Specialist, 2 Research Specialists, 3 Productivity Specialists, 1 Creative Specialist, 1 Communication Specialist, 1 Automation Specialist.
  - 32 Granular Specialist Capabilities across recruitment (9), computer (4), coding (3), research (3), productivity (7), creative & communication (4), and automation (2), all registered in `CapabilityRegistry` with deterministic analytical fallbacks.
  - Hardware Guardrail Compliance: Calibration for NVIDIA RTX 4050 6GB Laptop GPU utilizing AI Gateway's single-active-model semaphore (`asyncio.Semaphore(1)`) and maximum 4 concurrent analytical workers (`Semaphore(4)`).
  - Multi-Agent Collaboration DAGs: End-to-end recruitment analysis & resume tailoring workflow, and static code review & automated test generation pipeline.
  - Persistence & Telemetry: `AgentConfigurationRecord` in SQLite, execution tracking, dynamic runtime configuration updates (`PATCH /api/v1/agents/{id}/configuration`), and per-agent live diagnostics (`POST /api/v1/agents/{id}/test`).
  - Desktop Agents Workspace (`/agents`): Real-time manifest loading, category filtering tabs (Orchestration, Recruitment, Computer, Coding, Research, Productivity, Creative, Comms, Automation), status badges, and 4-tab interactive detail inspector (Overview, Configuration, History, Diagnostics).
  - 10 new architectural documents (`SPECIALIST_AGENT_FRAMEWORK.md`, `SPECIALIST_AGENT_CATALOG.md`, `AGENT_MANIFESTS.md`, `AGENT_MODEL_PROFILES.md`, `RECRUITMENT_AGENTS.md`, `COMPUTER_AGENTS.md`, `PRODUCTIVITY_AGENTS.md`, `CREATIVE_AND_COMMUNICATION_AGENTS.md`, `AGENT_SECURITY.md`, `AGENT_TESTING.md`).
- **Acceptance Criteria**: 94/94 Pytest unit & integration tests passed; 112/112 Vitest frontend tests passed; clean TypeScript typecheck across monorepo; clean production build. Ready for Stage 14. DO NOT begin Stage 14 until explicitly instructed.

#### Stage 14: Advanced Authorization Engine, Granular Permissions, Preauthorized Autonomy, Approval Workflows, Policy Enforcement, Emergency Stop, Secure Tool Execution, and Comprehensive Audit Logging [COMPLETE]

- **Status**: COMPLETE (2026-11-18)
- **Goal**: Establish a production-grade, centralized, deterministic Authorization Engine controlling autonomous agent execution, bounding agent capabilities, managing standing preauthorizations, queueing human-in-the-loop approvals, providing hard emergency stop controls, securing tool execution boundaries, and maintaining an append-only audit ledger.
- **Key Deliverables**:
  - Deterministic Authorization Engine (`AuthorizationEngine`) enforcing 10 evaluation precedence steps: Emergency Stop -> Automation Pause -> Credential Invariants -> Pre-existing Approvals -> Standing Grants -> Explicit Deny Policies -> Require Approval Policies -> Explicit Allow Policies -> Low-Risk Read Baseline -> High-Risk Action Guard -> Default Deny.
  - 6 Relational SQLite tables: `authorization_policies`, `authorization_policy_versions`, `authorization_grants`, `approval_requests`, `authorization_decisions`, `emergency_stop_state`.
  - 10 Permission Categories (`recruitment`, `filesystem`, `network`, `credential`, `browser`, `desktop`, `communication`, `code`, `creative`, `system`) and 4 Risk Levels (`LOW`, `MODERATE`, `HIGH`, `CRITICAL`).
  - 6 Immutable Baseline Policies: System Read-Only Baseline, Moderate Synthesis Baseline, Credential Access Strict Isolation, External Job Application Submission Gate, Outbound Communications Gate, Destructive Operations Gate.
  - Preauthorized Autonomy & Standing Grants (`AuthorizationGrant`): Time-bounded, usage-capped, workflow-scoped, and resource-bounded authorizations for uninterrupted autonomous operations.
  - Durable Human-in-the-Loop Approval Queue (`ApprovalRequest`): SHA-256 parameter digest deduplication, expiration sweeping, single-use `consumed` state preventing parameter replay attacks.
  - Fail-Closed Global Emergency Stop & Automation Pause (`EmergencyStopController`): Thread-safe in-memory caching synchronized with persistent SQLite state, surviving application restarts.
  - Secure Tool Execution Gateway (`ToolExecutionGateway`): Enforcement barrier wrapping all capability invocations, pre-execution checks, just-in-time TOCTOU emergency stop checks, approval consumption, and audit trail emission.
  - Workflow Integration: `ExecutionScheduler` pauses step on `AuthorizationRequiredError`, marks workflow `WAITING_FOR_AUTHORIZATION`, and resumes cleanly upon operator approval.
  - Desktop Frontend Workspace (`/approvals`): Pending approvals queue, approval inspector drawer, policy manager, standing grants manager, audit ledger, and emergency stop modal.
  - Command Center Integration: Emergency Stop button and Pause toggle in `DashboardHeader`, live pending approvals alert in `PendingActionsPanel`.
  - Desktop Tray Integration: System tray menu items for Emergency Stop, Pause Automation, and Pending Approvals Queue.
  - 11 Architectural Documents: `AUTHORIZATION_ENGINE.md`, `PERMISSION_MODEL.md`, `POLICY_SCHEMA.md`, `AUTONOMOUS_GRANTS.md`, `APPROVAL_WORKFLOWS.md`, `TOOL_EXECUTION_SECURITY.md`, `EMERGENCY_STOP.md`, `RECRUITMENT_AUTHORIZATION.md`, `SECURITY_AUDIT.md`, `PROMPT_INJECTION_DEFENSES.md`, `AUTHORIZATION_TESTING.md`.
  - Automated Verification: 113/113 pytest tests passing (100%), 121/121 Vitest tests passing (100%), clean TypeScript typecheck across monorepo, clean production Vite build.
- **Acceptance Criteria**: All Stage 14 requirements satisfied with zero mock data and strict fail-closed security. Ready for Stage 15.

#### Stage 15: Persistent Agent Memory, Hybrid Semantic Retrieval, Local Embeddings, Episodic and Procedural Knowledge, Memory Consolidation, Context Engineering, Privacy-Aware Retrieval, and Long-Term Learning [COMPLETED]

- **Goal**: Persistent cognitive agent memory architecture with hybrid semantic retrieval, deterministic local embeddings, episodic experience learning, procedural workflows, and privacy-aware access controls.
- **Key Deliverables**:
  - Memory Database Models: `MemoryRecord`, `MemoryEmbeddingRecord`, `MemoryConflictRecord`, `ProceduralMemoryRecord`, `MemoryAccessEventRecord`, and `memory_fts` SQLite FTS5 table.
  - Central Memory Service (`services/api/app/memory/service.py`) coordinating write pipeline, deduplication, conflict resolution, and access audit logging.
  - Cognitive Memory Taxonomy: Working Memory, Episodic Memory, Semantic Memory, and Procedural Memory.
  - Local-First Embedding Engine: Deterministic, zero-network 384-dimensional unit vector generator (<1ms) and Ollama adapter with automated fallback.
  - Vector Storage: In-memory normalized cosine similarity index synchronized with persistent SQLite tables.
  - Hybrid Retrieval Engine: SQLite FTS5 BM25 keyword matching fused with dense vector cosine similarity via Reciprocal Rank Fusion (RRF) and epistemic verification weighting.
  - Context Builder: Prompt section layout (`[VERIFIED FACTS]`, `[REUSABLE PROCEDURES]`, `[EPISODIC EXPERIENCES]`) with token budget limits.
  - Lifecycle Services: Deduplication (SHA-256 hash), conflict detection, supersession linking, consolidation, expiration sweeps, and cascading deletion.
  - Agent Integrations: Supervisor planning enrichment, specialist-agent scoped queries (Recruitment, Coding, Research, Creative).
  - REST APIs: 20 typed endpoints in `services/api/app/api/v1/endpoints/memory.py` for search, CRUD, conflicts, procedures, and stats.
  - Desktop Frontend Workspace: Full React workspace (`/memory`) with Overview Dashboard, Memory Explorer, Semantic Search, Procedural Knowledge, Conflict Review, and Diagnostics.
  - Automated Verification: 125/125 pytest tests passing (100%), 126/126 Vitest tests passing (100%), clean TypeScript typecheck, and clean production Vite bundle.
- **Acceptance Criteria**: Phase 3 AI Intelligence Engine is 100% complete. Ready for Phase 4.

---

### Phase 4: Computer and Browser Automation (Stages 16–30)

#### Stage 16: Production-Oriented Browser Automation, Playwright Integration, Browser Session Management, DOM Interaction, Web Navigation, Secure Authentication, Downloads, Execution Recovery, and Multi-Agent Browser Control [COMPLETE]

- **Status**: COMPLETE (2026-11-18)
- **Goal**: Implement a production-grade browser automation engine based on Playwright, enabling multi-agent navigation, session isolation, token-efficient DOM extraction, form field classification, DPAPI-encrypted authentication profiles, safe file downloads with SHA-256 verification, execution recovery, and desktop live controller workspace.
- **Key Deliverables**:
  - Playwright browser runtime manager with automatic discovery of bundled Chromium, Microsoft Edge, and Google Chrome on Windows 11.
  - Context isolation architecture with multi-tab management, popup interception, and deduplication.
  - Origin security validator blocking `file:`, `javascript:`, private RFC 1918 subnets, and cloud metadata addresses (`169.254.169.254`, `metadata.google.internal`).
  - Windows DPAPI-encrypted browser profiles protecting session cookies and local storage.
  - Interactive DOM extractor with 94-98% token reduction and smart multi-strategy locators (`role=`, `text=`, `placeholder=`, `label=`, `test-id=`, CSS, XPath).
  - Form analyzer mapping form controls to verified applicant profile data with submission boundary checks.
  - Safe download manager with size quota enforcement, filename sanitization, SHA-256 hash tracking, and isolated storage.
  - 9 registered browser capabilities and `browser_agent` upgraded to `AvailabilityState.OPERATIONAL`.
  - 20 typed REST endpoints under `/api/v1/browser/` with fail-closed Emergency Stop integration.
  - Desktop frontend workspace (`/computer/live` under `'browser'` tab) with Overview, Live Controller, DOM Inspector, Downloads, and Profiles.
  - 11 architectural documents (`BROWSER_AUTOMATION_ARCHITECTURE.md`, `BROWSER_RUNTIME.md`, `BROWSER_SESSIONS.md`, `BROWSER_AUTHENTICATION.md`, `DOM_INTERACTION.md`, `BROWSER_TOOL_CONTRACTS.md`, `BROWSER_SECURITY.md`, `BROWSER_DOWNLOADS.md`, `BROWSER_RECOVERY.md`, `BROWSER_AGENT_INTEGRATION.md`, `BROWSER_TESTING.md`).
  - Automated Verification: 145/145 pytest backend tests passing (100%), 131/131 Vitest desktop tests passing (100% across 34 files), clean TypeScript typecheck across monorepo, clean Vite production build.
- **Acceptance Criteria**: All Stage 16 requirements satisfied with zero fake data and fail-closed security. Ready for Stage 17. DO NOT begin Stage 17 until explicitly instructed.

#### Stage 17: Windows Structural UI Automation, Native Application Control & Accessibility Tree Inspection

- **Status**: COMPLETE
- **Goal**: Full structural control of Microsoft Windows desktop applications via Microsoft UI Automation (UIA) and Win32 APIs, eliminating coordinate-based fragile vision clicking.
- **Key Deliverables**:
  - Native Windows interactive session discovery, lock state detection (`OpenInputDesktop`), and screen resolution tracking.
  - Native top-level window discovery via `EnumDesktopWindows` with compound reference tracking (`window_ref = win_{hwnd}_{pid}`) and recycled HWND defense.
  - Dedicated Multi-Threaded Apartment (MTA) COM worker supervisor (`UIAWorkerSupervisor`) with desktop attachment (`SetThreadDesktop`) preventing thread affinity deadlocks.
  - Bounded accessibility tree inspection (`UITreeInspector`) supporting depth bounds, node limits, and compact outline compilation (`UISnapshotCompiler`) for token-efficient LLM agent reasoning.
  - Semantic element locators (`LocatorResolver`) and typed pattern execution (`PatternExecutor`) covering `Invoke`, `Value`, `Toggle`, `SelectionItem`, `ExpandCollapse`, and `Scroll`.
  - Legacy Win32 messaging fallback (`Win32CompatibilityAdapter`) and focused keyboard input adapter.
  - Defense-in-depth security: fail-closed Emergency Stop, approved application allowlists (`DEFAULT_ALLOWED_APPS`), token integrity level enforcement, path traversal guard (`FileDialogSafetyGuard`), and sensitive data masking (`PrivacyFilter`).
  - Post-action mutation verification (`StructuralActionVerifier`) asserting state mutations.
  - 9 registered desktop capabilities in capability registry; `windows_computer_agent` and `structural_ui_agent` upgraded to `AvailabilityState.OPERATIONAL`.
  - 18 typed REST endpoints under `/api/v1/desktop/*` with full authentication enforcement.
  - Desktop frontend workspace (`/computer` under `'desktop'` tab) with Overview, Applications, Windows, UI Tree Inspector, Action History, Tasks, and Diagnostics.
  - 10 architectural documents (`WINDOWS_AUTOMATION_ARCHITECTURE.md`, `UI_AUTOMATION_ENGINE.md`, `UIA_COM_THREADING.md`, `WINDOW_DISCOVERY.md`, `ACCESSIBILITY_TREE_INSPECTION.md`, `DESKTOP_ACTION_CONTRACTS.md`, `WINDOWS_AUTOMATION_SECURITY.md`, `DESKTOP_RECOVERY.md`, `COMPUTER_AGENT_INTEGRATION.md`, `WINDOWS_AUTOMATION_TESTING.md`).
  - Automated Verification: 166/166 pytest backend tests passing (100%), 134/134 Vitest desktop tests passing (100% across 35 files), clean TypeScript typecheck across monorepo, clean Vite production build.
- **Acceptance Criteria**: All Stage 17 requirements satisfied with zero fake data and fail-closed security. Ready for Stage 18. DO NOT begin Stage 18 until explicitly instructed.

#### Stage 18: Visual Computer Control, Windows Screen Capture, Vision-Language Models, OCR, Visual UI Grounding, Coordinate-Based Interaction, Continuous Observation, and Visual Action Verification

- **Status**: COMPLETE
- **Goal**: Implement genuine visual desktop automation using real Windows screen capture, offline WinRT OCR, visual grounding, coordinate-based interaction, continuous observation, and visual action verification.
- **Key Deliverables**:
  - Pluggable capture engine supporting MSS, GDI PrintWindow, and Windows Graphics Capture with thread-safe interactive desktop attachment.
  - Offline WinRT Optical Character Recognition (`winsdk.windows.media.ocr`) with fuzzy target search and automated category classification.
  - Coordinate transformation engine mapping model space -> raw frame -> physical desktop -> Windows SendInput 0..65535 space with inward margin offsetting.
  - Visual UI grounding pipeline combining OCR text detection, visual heuristics, ambiguity detection, and safe target validation.
  - Windows `SendInput` mouse and keyboard adapter with exclusive concurrency ownership leases (`InputOwnershipManager`).
  - Pre- and post-action visual verification (`VisualActionVerifier`) measuring pixel difference percentages and verifying expected text mutations.
  - Bounded recovery manager (`VisualRecoveryManager`) with jittered exponential backoffs, target re-grounding, and fallback strategies.
  - Deterministic visual task state machine (`VisualStateMachine`) managing task lifecycles from observing to verified completion.
  - Fail-closed security guard (`VisualSecurityGuard`) with physical `Pause/Break` killswitch, REST API killswitch, session lock detection, and credential masking.
  - 9 registered visual capabilities; `visual_grounding_agent` promoted to `AvailabilityState.OPERATIONAL`.
  - 19 authenticated REST API endpoints under `/api/v1/visual/*`.
  - Comprehensive desktop frontend workspace (`/computer` under `'visual'` tab) with Overview, Capture, Grounding, Actions, Tasks, and Diagnostics tabs.
  - 12 comprehensive architectural and operational documents.
  - Automated Verification: 189/189 pytest backend tests passing (100%), Vitest tests passing (100%), clean TypeScript typecheck across monorepo, clean Vite production build (2449 modules).
- **Acceptance Criteria**: All Stage 18 requirements satisfied with genuine Windows screen capture, offline OCR, verified coordinate transforms, and fail-closed security. Ready for Stage 19. DO NOT begin Stage 19 until explicitly instructed.

#### Stage 19: Intelligent Hybrid Computer Interaction Engine, Multi-Method Control Routing, DOM + UIA + Vision Integration, Context-Aware Fallback, Unified Action Execution, and Cross-Application Coordination [COMPLETED]

- **Status**: COMPLETE
- **Goal**: Unify Stage 16 (Playwright Browser DOM), Stage 17 (Windows UIA/Win32 Structural Control), and Stage 18 (Visual Grounding & WinRT OCR) into a cohesive, production-grade Hybrid Computer Interaction Engine capable of deterministic method routing, unified target classification, context-aware fallback with bounded switch limits, multi-method mutual exclusion leases, and seamless Stage 14 policy-enforced security boundaries.
- **Key Deliverables**:
  - Unified Target Identity & Surface Classifier (`SurfaceClassifier`, `TargetIdentityValidator`, `TargetResolver`) supporting recycled HWND defense, DOM selector validation, coordinate bounds checking, and automatic surface classification across `BROWSER_DOM`, `NATIVE_UIA`, `NATIVE_WIN32`, `CUSTOM_RENDERED`, `EMBEDDED_WEBVIEW`, and `UNKNOWN`.
  - Normalized Interaction Adapters (`BrowserDOMAdapter`, `WindowsUIAAdapter`, `Win32Adapter`, `VisualAdapter`) implementing the unified `InteractionAdapter` protocol with concurrent probing and health tracking (`InteractionAdapterRegistry`, `MethodHealthTracker`).
  - Dynamic Control Routing Engine (`HybridMethodRouter`, `MethodScorer`, `RoutingPolicies`) with transparent 0..100 scoring across capability fit (40%), reliability (25%), cost (15%), and surface preference bonus (20%), generating explainable `RoutingDecisionRecordSchema`.
  - Context-Aware Fallback Engine (`FallbackController`) enforcing bounded switch depth (max 3), loop prevention, mandatory pre-fallback re-observation, and non-idempotent action protections against replaying uncertain mutations.
  - Cross-Method Observation Coordinator (`ObservationCoordinator`) merging structural trees, text, and on-demand visual perception into normalized `InteractionObservation` models with stale cache invalidation.
  - Multi-Method Execution & Input Lease Coordinator (`HybridActionCoordinator`, `HybridInputOwnershipCoordinator`, `HybridVerificationCoordinator`, `HybridStateMachine`) coordinating exclusive foreground leases for physical input (`SendInput` / Win32) while allowing concurrent non-intrusive operations.
  - Fail-Closed Security & Authorization Integration (`HybridExecutionGuard`, `HybridAuthorizationBridge`) binding Stage 14 Emergency Stop, Win32 workstation session lock detection (`OpenInputDesktop`), and granular action category permission checks without privilege escalation on fallback.
  - 9 Registered Hybrid Capabilities (`hybrid_resolve_target`, `hybrid_probe_methods`, `hybrid_route_action`, `hybrid_observe`, `hybrid_execute`, `hybrid_click`, `hybrid_type`, `hybrid_fallback`, `hybrid_execute_task`) promoting `windows_computer_agent` (v1.1.0) to primary desktop coordinator.
  - 18 Authenticated REST API Endpoints under `/api/v1/hybrid/*`.
  - Comprehensive Desktop Frontend Workspace (`/computer/hybrid`) featuring Hybrid Overview, Capability Matrix, Routing Policy Simulator, Unified Sessions Telemetry, Hybrid Tasks Dispatcher, and Diagnostics & Audit Ledger.
  - 11 Architectural & Operational Documents in `docs/`.
  - Automated Verification: 40/40 hybrid backend tests passed (100%), 229/229 full backend test suite passed (100%), 146/146 frontend vitest tests passed (100% across 37 files), clean TypeScript typecheck across monorepo, clean Vite production build (2456 modules transformed).
- **Acceptance Criteria**: All Stage 19 requirements satisfied with zero fake data, deterministic routing, safe bounded fallback, fail-closed security, and verified desktop UI. Ready for Stage 20. DO NOT begin Stage 20 until explicitly instructed.

#### Stage 20: Audit Logging, Decision Lineage & Replay Debugger

- **Goal**: Comprehensive immutable audit trail capturing every decision, prompt, tool execution, and state change with step-by-step replay capability.
- **Key Deliverables**:
  - Append-only audit log store in SQLite.
  - Decision lineage graph linking user intent to sub-agent actions.
  - Replay viewer in desktop UI allowing visual inspection of past executions.
- **Acceptance Criteria**: Complete audit log generated for every agent run; replay viewer reconstructs exact execution timeline.

---

### Phase 3: Dual Computer Interaction — Visual Grounding & Structural Automation (Stages 21–30)

#### Stage 21: High-Performance Screen Capture & Multi-Monitor Display Pipeline

- **Goal**: Native Windows screenshot capture pipeline supporting multi-monitor configurations, high-DPI scaling, and sub-100ms capture latency.
- **Key Deliverables**:
  - Desktop Duplication API / Windows Graphics Capture wrapper in Rust / Python.
  - Virtual desktop and per-monitor coordinate normalization.
  - Real-time frame downsampler and JPEG/WebP optimizer for vision models.
- **Acceptance Criteria**: Captures primary and secondary displays at native resolution with accurate scaling in under 100ms.

#### Stage 22: Visual Grounding Engine (Vision Coordinates, OCR & Template Matching)

- **Goal**: Multimodal visual grounding engine translating natural language element descriptions into pixel coordinates using vision models, OCR, and OpenCV.
- **Key Deliverables**:
  - Windows Media OCR / Tesseract / EasyOCR integration for text bounding boxes.
  - Vision model bounding box parser (e.g., Gemini Vision, Claude 3.5 Sonnet).
  - OpenCV template matching for standard Windows UI icons.
- **Acceptance Criteria**: Given an instruction like "Click the Submit button", engine identifies target coordinates with >95% accuracy on test screens.

#### Stage 23: Native OS Input Injection & Human-like Trajectory Controller

- **Goal**: Windows input controller using `SendInput` API with natural Bézier mouse movement curves, variable typing delays, and modifier key support.
- **Key Deliverables**:
  - Native Windows `SendInput` wrapper for mouse move, click, drag, scroll, and key press.
  - Bézier curve trajectory generator with micro-jitter and randomized acceleration.
  - Anti-detection typing simulator with realistic inter-keystroke latencies.
- **Acceptance Criteria**: Executes smooth mouse movements and typing into target windows without triggering synthetic input drops.

#### Stage 24: Windows UI Automation (UIA) Structural Inspector & Accessibility Tree

- **Goal**: Structural interaction client accessing the native Windows UI Automation (UIA) tree via COM interfaces to inspect controls and properties.
- **Key Deliverables**:
  - COM-based UIA client (using `UIAutomationClient` / `pywinauto` / `uiautomation`).
  - Accessibility tree serializer producing compact structural representations.
  - Control search by AutomationId, Name, ClassName, ControlType, and XPath.
- **Acceptance Criteria**: Locates desktop application windows, buttons, text inputs, and tables by structural attributes in <50ms.

#### Stage 25: Structural Control & Pattern Invocation Engine

- **Goal**: Directly invoke UIA control patterns (InvokePattern, ValuePattern, SelectionItemPattern, ScrollPattern, TogglePattern) without moving the mouse.
- **Key Deliverables**:
  - Pattern invocation engine for immediate value setting and button clicks.
  - Window focus, maximize, minimize, and restore controller.
  - Background window interaction without stealing active foreground focus.
- **Acceptance Criteria**: Fills text fields and triggers button clicks directly via UIA patterns while window is in the background.

#### Stage 26: Playwright Browser Headless/Headed Driver & Automation Engine

- **Goal**: Integrated Playwright browser manager supporting Chromium, Firefox, and WebKit with persistent user profiles and stealth capabilities.
- **Key Deliverables**:
  - Playwright driver manager with automated browser binary provisioning.
  - Persistent browser context preserving cookies, local storage, and session state.
  - Stealth configuration preventing bot detection headers and navigator flags.
- **Acceptance Criteria**: Launches persistent browser session, navigates complex single-page apps, and maintains logged-in state across restarts.

#### Stage 27: Hybrid Vision-Structural Interaction Arbiter

- **Goal**: Decision arbiter selecting optimal interaction modality: structural (DOM/UIA) when reliable, visual (screenshot/grounding) when structural tree is inaccessible.
- **Key Deliverables**:
  - Modality selector scoring confidence of DOM/UIA selectors vs. visual grounding.
  - Automatic fallback cascade (UIA/DOM -> Visual Grounding -> Error Recovery).
  - Unified interaction command API (`click_element`, `fill_field`, `select_option`).
- **Acceptance Criteria**: Seamlessly transitions between DOM automation and visual coordinate clicks when encountering canvas/custom controls.

#### Stage 28: Safe Interaction Guardrails & Forbidden Zones

- **Goal**: Safety boundary system preventing accidental clicks in sensitive areas (system trays, taskbars, close buttons, external apps) and handling CAPTCHAs.
- **Key Deliverables**:
  - Screen boundary mask defining allowed application bounding boxes.
  - Anti-bot / CAPTCHA detector immediately pausing automation and alerting user.
  - Emergency abort hotkey (e.g., `Ctrl+Esc` / `F12`) instantly halting all input injection.
- **Acceptance Criteria**: Input injection strictly blocked outside target application boundaries; CAPTCHA detection pauses automation and notifies user.

#### Stage 29: Desktop Visual Action Recording & Macro Playback Engine

- **Goal**: Record user desktop demonstrations (mouse clicks, typing, window focus) and compile them into reusable, parameterized agent automation macros.
- **Key Deliverables**:
  - Windows global hook event recorder capturing inputs and screenshot snapshots.
  - Macro optimizer merging micro-events into high-level semantic actions.
  - Parameterized macro player with variable substitution.
- **Acceptance Criteria**: Records user completing a web form and successfully replays it with new input parameters.

#### Stage 30: Computer Use Verification & Post-Action State Asserter

- **Goal**: Verification engine validating that intended state changes actually occurred after an input action before proceeding.
- **Key Deliverables**:
  - Visual difference calculator comparing pre- and post-action screenshots.
  - DOM/UIA state change poller checking for expected elements (e.g., success message).
  - Verification assertion DSL (`assert_element_exists`, `assert_text_changed`).
- **Acceptance Criteria**: Flags failed form submissions despite successful button clicks by detecting missing confirmation screens.

---

### Phase 4: Autonomous Job Discovery, Tailoring, Application & Outreach (Stages 31–40)

#### Stage 31: User Career Profile & Identity Store

- **Goal**: Structured, verifiable user profile repository capturing work experience, education, verified skills, publications, and projects with strict non-fabrication guarantees.
- **Key Deliverables**:
  - Career profile schema with strict factual constraints.
  - Profile editor UI with validation against unsupported claims.
  - Encrypted local profile storage with export/import capabilities.
- **Acceptance Criteria**: Profile schema enforces structured factual records; system strictly prevents agent from adding unverified skills or past employers.

#### Stage 32: Resume Parser, AST Representation & Multi-Format Ingestion

- **Goal**: Parse PDF, DOCX, and Markdown resumes into an Abstract Syntax Tree (AST) representing sections, employment dates, bullet points, and credentials.
- **Key Deliverables**:
  - Multi-format document parser (`pdfplumber` / `pypdf` / `python-docx`).
  - Resume AST data structure with section and item granularity.
  - Visual resume preview in desktop UI with parsed structure inspector.
- **Acceptance Criteria**: Accurately parses user's real resume into structured AST with zero missing sections or scrambled bullet points.

#### Stage 33: Multi-Platform Job Discovery Scraper & Aggregator

- **Goal**: Automated job search scraper querying LinkedIn, Indeed, Glassdoor, Greenhouse, Lever, and Workday based on user criteria.
- **Key Deliverables**:
  - Platform-specific scrapers using Playwright and public APIs.
  - Rate limiting, randomized delays, and session management.
  - Deduplication pipeline identifying identical postings across multiple boards.
- **Acceptance Criteria**: Discovers and aggregates >50 unique job postings matching query criteria across at least 3 platforms.

#### Stage 34: Job Extraction, Normalization & Semantic Parsing Engine

- **Goal**: Extract and normalize job posting attributes: job title, company, salary ranges, location/remote type, required experience, tech stack, and visa sponsorship.
- **Key Deliverables**:
  - LLM-powered structured extractor parsing raw job HTML/text.
  - Normalized job entity model with standardized seniority and location classifications.
  - Jobs exploration UI with filtering, sorting, and full text search.
- **Acceptance Criteria**: Normalizes raw job descriptions with >95% accuracy in salary, location, and requirement extraction.

#### Stage 35: Job Matching, Semantic Fit Scoring & Gap Analysis Engine

- **Goal**: Semantic matching engine computing compatibility scores between user profile and job requirements, highlighting matching qualifications and gaps.
- **Key Deliverables**:
  - Embedding-based semantic similarity and requirement checklist matcher.
  - Match score breakdown (Skills match, Experience match, Education match, Location fit).
  - Factual gap analysis explaining missing required criteria.
- **Acceptance Criteria**: Generates transparent match scores and detailed gap analyses without hallucinating user qualifications.

#### Stage 36: Factual Resume Tailoring & Targeted Cover Letter Generator

- **Goal**: Dynamically reorder, rephrase, and emphasize existing factual achievements to align with specific job descriptions, exporting to ATS-friendly PDF.
- **Key Deliverables**:
  - Factual alignment engine re-weighting existing bullet points based on JD keywords.
  - Strict anti-hallucination constraint ensuring every output bullet maps to original source.
  - LaTeX / HTML-to-PDF renderer producing clean, ATS-compliant PDF resumes.
- **Acceptance Criteria**: Tailored resume contains 100% verified factual statements from user profile; output PDF passes ATS readability checks.

#### Stage 37: Application Form Field Classifier & Autofill Knowledge Engine

- **Goal**: Machine-learning and heuristic classifier identifying standard application form fields (Personal Info, EEO, Work Auth, Experience, Custom Questions).
- **Key Deliverables**:
  - Form field classifier mapping input elements to user profile attributes.
  - Custom question answer bank retrieving prior approved user answers.
  - Fallback prompt asking user for answers to novel company-specific questions.
- **Acceptance Criteria**: Correctly classifies form fields on Greenhouse, Lever, and Workday forms with >98% accuracy.

#### Stage 38: End-to-End Autonomous Application Submitter

- **Goal**: Autonomous browser agent filling and submitting job applications through ATS portals with configurable advance authorization and human approval checkpoints.
- **Key Deliverables**:
  - Full application workflow (Navigation -> File Upload -> Form Fill -> Review -> Submission).
  - Human-in-the-loop review modal displaying filled fields before final submission click.
  - Post-submission confirmation capture (receipt screenshot and application ID).
- **Acceptance Criteria**: Successfully completes and submits real applications on Greenhouse/Lever demo environments with full audit trail.

#### Stage 39: Email Integration & Application Correspondence Tracker

- **Goal**: Monitor user's job-search email inbox via IMAP / OAuth to track application acknowledgments, interview invitations, and status updates.
- **Key Deliverables**:
  - Email parser classifying incoming messages (Received, Under Review, Interview Request, Rejection).
  - Application status state machine updating job records automatically.
  - Interview scheduling assistant extracting suggested dates and calendar links.
- **Acceptance Criteria**: Accurately categorizes incoming recruitment emails and updates application status in the database.

#### Stage 40: Interview Preparation Engine & Company Research Dossier

- **Goal**: Compile comprehensive interview preparation dossiers including company history, executive team, recent news, culture, and role-specific technical Q&A.
- **Key Deliverables**:
  - Automated research synthesizer gathering company data and interview reviews.
  - Role-specific behavioral and technical question generator based on job description.
  - Interactive interview practice flashcard and mock interview interface in desktop UI.
- **Acceptance Criteria**: Generates comprehensive interview prep dossier for a target role within 60 seconds.

---

### Phase 5: Extended Workspace Tools, Media, 3D, Production Hardening & Packaging (Stages 41–50)

#### Stage 41: Local Workspace Code Automation & Script Execution

- **Goal**: Secure agent tool allowing local script execution (Python, PowerShell, Bash, Node.js) and Git operations within a controlled workspace directory.
- **Key Deliverables**:
  - Sandboxed command runner with workspace directory confinement.
  - Git repository operator (clone, branch, commit, status).
  - Real-time stdout/stderr streaming to agent context.
- **Acceptance Criteria**: Executes automation scripts securely within designated workspace; prevents execution outside authorized directory.

#### Stage 42: Autonomous Web Research & Synthesis Engine

- **Goal**: Multi-step deep research agent capable of browsing technical documentation, querying search engines, synthesizing findings, and exporting research reports.
- **Key Deliverables**:
  - Web search tool integration with citation tracking.
  - Multi-page scraper extracting clean markdown content.
  - Markdown report compiler with executive summary, citations, and key insights.
- **Acceptance Criteria**: Produces cited technical research dossier answering complex questions using verified web sources.

#### Stage 43: Document & Presentation Generator (DOCX, PDF, PPTX)

- **Goal**: Automated document and slide generation tools creating professional portfolios, reports, and presentation decks.
- **Key Deliverables**:
  - `python-docx` template-based document builder.
  - `python-pptx` automated slide deck generator with structured layouts.
  - Document export and preview UI in the desktop application.
- **Acceptance Criteria**: Generates well-formatted, professional PPTX slides and DOCX reports from structured agent data.

#### Stage 44: Spreadsheet Data Analysis & Report Engine (XLSX)

- **Goal**: Spreadsheet automation tool reading, analyzing, generating, and formatting Excel workbooks with formulas, summary statistics, and charts.
- **Key Deliverables**:
  - `openpyxl` / `pandas` spreadsheet operator.
  - Automated formula injection (SUM, AVERAGE, XLOOKUP, pivot tables).
  - Data table visualization component in desktop UI.
- **Acceptance Criteria**: Reads job tracking data, generates formatted XLSX workbook with formulas, and visualizes summary charts.

#### Stage 45: 3D Asset & Graphics Tool Integration (Blender CLI & Three.js Preview)

- **Goal**: Integrate 3D visualization and asset processing via Blender command line and embedded Three.js / WebGL viewport in the desktop UI.
- **Key Deliverables**:
  - Headless Blender script generator for asset rendering and conversion.
  - WebGL / Three.js 3D viewer component in React frontend.
  - 3D asset inspection and metadata extraction tool.
- **Acceptance Criteria**: Renders 3D model preview interactively in desktop UI and executes headless Blender rendering scripts.

#### Stage 46: Media, Animation & Visual Content Pipeline

- **Goal**: Automated media processing pipeline supporting video trimming, audio normalization, subtitle generation, and FFmpeg command automation.
- **Key Deliverables**:
  - FFmpeg command builder and runner for video/audio conversion.
  - Media asset metadata inspector and waveform visualizer.
  - Media preview pane in desktop UI.
- **Acceptance Criteria**: Transcodes video/audio clips, generates subtitles, and displays interactive media playback in UI.

#### Stage 47: Communications, Messaging & Webhook System

- **Goal**: Outbound and inbound messaging integrations supporting Slack, Discord, Telegram, and custom HTTP webhooks for real-time notifications.
- **Key Deliverables**:
  - Webhook dispatcher with retry policy and HMAC signature verification.
  - Slack and Discord bot connectors for remote agent status checks and approvals.
  - Notification preference center in desktop settings.
- **Acceptance Criteria**: Dispatches rich status alerts and interactive approval prompts to Slack/Discord webhooks upon critical events.

#### Stage 48: End-to-End Integration Testing & Resilience Stress Suite

- **Goal**: Rigorous stress testing suite evaluating system performance under network dropouts, heavy concurrent workloads, and unexpected process crashes.
- **Key Deliverables**:
  - Chaos test suite simulating network timeouts, API rate limits, and crash events.
  - End-to-end multi-agent test scenario covering discovery through application submission.
  - Automated test runner generating comprehensive pass/fail test reports.
- **Acceptance Criteria**: System recovers autonomously from 100% of simulated transient errors without data corruption or deadlocks.

#### Stage 49: Performance Profiling, Memory Optimization & Windows Footprint Tuning

- **Goal**: Fine-tune application memory footprint, cold-start time, CPU utilization, and battery efficiency for background Windows operation.
- **Key Deliverables**:
  - Memory leak detection and cleanup in Rust, Python, and React layers.
  - Bundle size reduction (code splitting, tree shaking, lazy loading).
  - Background power state throttling reducing idle CPU usage to <1%.
- **Acceptance Criteria**: Desktop cold start < 2.0s; idle memory footprint < 150MB; idle CPU utilization < 1%.

#### Stage 50: Production Build, Code Signing, Windows MSIX / NSIS Installer & Release

- **Goal**: Final production build packaging, executable signing, MSIX/NSIS installer creation, auto-updater integration, and release distribution.
- **Key Deliverables**:
  - Tauri production build configuration with bundled Python runtime.
  - NSIS installer script with uninstaller, shortcuts, and registry entries.
  - Auto-update updater manifest and GitHub Releases integration.
- **Acceptance Criteria**: Production installer installs cleanly on fresh Windows 11 machine, launches all services, runs flawlessly, and uninstalls cleanly.
