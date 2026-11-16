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

#### Stage 09: System Tray, Windows Notifications & Window State Management

- **Goal**: Native Windows integration including system tray icon, background execution, native toast notifications, and window position persistence.
- **Key Deliverables**:
  - Tauri system tray with context menu (Open, Pause Agents, Active Jobs, Exit).
  - Windows 11 Action Center notification sender.
  - Window geometry persistence across application restarts.
- **Acceptance Criteria**: Minimizing to tray works smoothly; toast notifications trigger on key events; window geometry restores precisely.

#### Stage 10: Multi-Process Health Monitoring, Auto-Recovery & Crash Resilience

- **Goal**: Enterprise supervision architecture monitoring UI, native layer, and Python workers with automatic crash detection and state recovery.
- **Key Deliverables**:
  - Health check ping loop across all subsystems.
  - State snapshotting to SQLite prior to complex task execution.
  - Recovery manager restoring in-flight task state after process crashes.
- **Acceptance Criteria**: Forced termination of backend worker causes supervisor to restart backend within 2 seconds and resume pending queue tasks.

---

### Phase 2: Agent Orchestration Engine & Local/Cloud Intelligence Runtime (Stages 11–20)

#### Stage 11: Multi-Provider LLM Gateway

- **Goal**: Unified model router supporting OpenAI, Anthropic, Google Gemini, Ollama, and local ONNX/GGUF models with automatic failover and token counting.
- **Key Deliverables**:
  - Abstract model provider interface (`generate`, `stream`, `embed`).
  - Provider implementations with retry logic, rate limit handling, and latency tracking.
  - Cost and token usage accounting per agent and per task.
- **Acceptance Criteria**: Dynamic switching between local and cloud providers with verified failover when primary provider is unavailable.

#### Stage 12: Base Agent Runtime & Plan-Execute-Verify-Recover Architecture

- **Goal**: Core agent engine implementing structured reasoning: Goal Formulation -> Step Planning -> Execution -> Verification -> Error Recovery.
- **Key Deliverables**:
  - Agent state machine (Idle, Planning, Executing, Verifying, Recovering, Awaiting Approval, Done, Failed).
  - Structured plan representation with dependency graphs.
  - Verification predicates checking execution success before advancing steps.
- **Acceptance Criteria**: Agent creates verifiable multi-step execution plans and recovers from synthetic step failures without halting.

#### Stage 13: Memory Architecture (Context Window, Episodic SQLite & Semantic Vectors)

- **Goal**: Three-tier memory system: working context window, episodic task history in SQLite, and local semantic retrieval via vector embeddings.
- **Key Deliverables**:
  - Context window manager with intelligent message pruning and summarization.
  - Episodic memory logger capturing tool calls, results, and outcomes.
  - Local vector store (`sqlite-vec` or ChromaDB local) for semantic similarity search.
- **Acceptance Criteria**: Agent recalls relevant prior experiences during planning and retains context across multiple sessions.

#### Stage 14: Multi-Agent Coordination & Swarm Message Board

- **Goal**: Swarm coordination system where specialized agents (Job Scout, Resume Tailor, Outreach Coordinator, Browser Operator) collaborate via a shared board.
- **Key Deliverables**:
  - Coordinator agent delegating sub-tasks to specialist agents.
  - Inter-agent message passing protocol with typed messages.
  - Conflict resolution and outcome arbitration mechanism.
- **Acceptance Criteria**: Coordinator splits a compound task into parallel sub-tasks, dispatches to two workers, and combines results.

#### Stage 15: Agent Dynamic Tool Execution Engine & Sandboxed Execution

- **Goal**: Secure, typed tool execution environment with argument validation, permission checks, execution timeouts, and result truncation.
- **Key Deliverables**:
  - Tool decorator and registry with Pydantic parameter schemas.
  - Sandbox execution wrapper enforcing wall-clock timeouts and memory limits.
  - Automatic tool documentation generation for LLM system prompts.
- **Acceptance Criteria**: Tool calls execute with verified argument validation; runaway tools terminate cleanly upon reaching timeouts.

#### Stage 16: Model Context Protocol (MCP) Client Core & Server Discovery

- **Goal**: Implement Model Context Protocol (MCP) client supporting stdio and SSE transports to connect to third-party tools and data sources.
- **Key Deliverables**:
  - MCP client implementation following official spec (JSON-RPC 2.0).
  - Server configuration loader (command, arguments, environment).
  - Tool, resource, and prompt discovery and mapping to AUTONOM agent tools.
- **Acceptance Criteria**: Successfully connect to standard MCP servers (e.g., SQLite MCP, Filesystem MCP) and execute discovered tools.

#### Stage 17: Extensible Tool Registry & Dynamic Plugin Loading

- **Goal**: Dynamic plugin system allowing users to load custom Python or TypeScript tools without modifying core application code.
- **Key Deliverables**:
  - Plugin manifest format (`plugin.json`) specifying metadata, tools, and permissions.
  - Safe dynamic import and dependency verification system.
  - Plugin management UI in Settings with enable/disable toggles.
- **Acceptance Criteria**: Custom plugin dropped into `plugins/` directory is automatically discovered, verified, and exposed to agents.

#### Stage 18: Streaming Token Parser & Interactive Agent Console

- **Goal**: Real-time agent console in desktop UI showing streaming thoughts, tool invocation traces, diff views, and manual override controls.
- **Key Deliverables**:
  - Streaming token renderer with syntax highlighting and markdown parsing.
  - Collapsible tool invocation cards showing input arguments and execution output.
  - Manual pause, resume, and step-by-step debug controls.
- **Acceptance Criteria**: Agent stream renders smoothly at >30 tokens/second without UI stuttering; user can pause and step through actions.

#### Stage 19: Agent Evaluation, Self-Reflection & Error Recovery Strategies

- **Goal**: Autonomous diagnostic engine where agents reflect on failed tool outputs and execute programmatic recovery strategies.
- **Key Deliverables**:
  - Reflection loop analyzing failure logs and error codes.
  - Recovery playbook library (retry with backoff, alternate parameter search, fallback tool).
  - Maximum retry threshold and graceful failure escalation.
- **Acceptance Criteria**: Agent recovers from simulated external API 500 errors and missing DOM selectors using alternate strategies.

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
