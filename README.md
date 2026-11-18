# AUTONOM

AUTONOM is an enterprise-grade, multi-agent Windows 11 desktop application designed for autonomous job discovery, resume tailoring, application submission, email handling, interview preparation, dual-mode computer interaction (visual and structural), and extensible workspace automation.

## Architecture

- **Desktop Shell**: Tauri 2.x (Rust) + React 19 + TypeScript + Vite.
- **Backend Service**: Python 3.12+ / FastAPI asynchronous agent runtime managed with `uv`.
- **Database**: Local SQLite 3 with Write-Ahead Logging (WAL) and Windows DPAPI encrypted secret storage.
- **Computer Interaction**: Dual-modality engine:
  - Visual: High-speed screenshot capture, vision grounding, and Windows `SendInput`.
  - Structural: Windows UI Automation (UIA) COM accessibility tree and Playwright DOM engine.

## Documentation

- [Roadmap (50 Stages)](file:///e:/proooo/AUTO%20JOB/docs/ROADMAP.md)
- [Development Setup & Engineering Guide](file:///e:/proooo/AUTO%20JOB/docs/DEVELOPMENT_SETUP.md)
- [System Architecture](file:///e:/proooo/AUTO%20JOB/docs/ARCHITECTURE.md)
- [Requirements Specification](file:///e:/proooo/AUTO%20JOB/docs/REQUIREMENTS.md)
- [Multi-Agent System & Catalog (24 Agents)](file:///e:/proooo/AUTO%20JOB/docs/AGENTS.md)
- [Database Design & Schemas](file:///e:/proooo/AUTO%20JOB/docs/DATABASE_DESIGN.md)
- [Security & Autonomy Policy](file:///e:/proooo/AUTO%20JOB/docs/SECURITY.md)
- [API Contracts](file:///e:/proooo/AUTO%20JOB/docs/API_CONTRACTS.md)
- [Dual-Modality Computer Control](file:///e:/proooo/AUTO%20JOB/docs/COMPUTER_CONTROL.md)
- [UI/UX & Design Tokens](file:///e:/proooo/AUTO%20JOB/docs/UI_UX_SPECIFICATION.md)
- [Hardware Strategy & Resource Budget](file:///e:/proooo/AUTO%20JOB/docs/RESOURCE_BUDGET.md)
- [External Integrations](file:///e:/proooo/AUTO%20JOB/docs/INTEGRATIONS.md)
- [Architecture Decisions (ADRs)](file:///e:/proooo/AUTO%20JOB/docs/DECISIONS.md)
- [Database Implementation](file:///e:/proooo/AUTO%20JOB/docs/DATABASE_IMPLEMENTATION.md)
- [Database Migrations](file:///e:/proooo/AUTO%20JOB/docs/MIGRATIONS.md)
- [Secure Storage & DPAPI Vault](file:///e:/proooo/AUTO%20JOB/docs/SECURE_STORAGE.md)
- [Backup & Disaster Recovery](file:///e:/proooo/AUTO%20JOB/docs/BACKUP_AND_RECOVERY.md)
- [Data Retention Policy](file:///e:/proooo/AUTO%20JOB/docs/DATA_RETENTION.md)
- [Storage Operations Runbook](file:///e:/proooo/AUTO%20JOB/docs/STORAGE_OPERATIONS.md)
- [Windows Desktop Shell & Integration](file:///e:/proooo/AUTO%20JOB/docs/WINDOWS_DESKTOP.md)
- [Backend Sidecar Architecture](file:///e:/proooo/AUTO%20JOB/docs/BACKEND_SIDECAR.md)
- [Process Lifecycle & Supervision](file:///e:/proooo/AUTO%20JOB/docs/PROCESS_LIFECYCLE.md)
- [System Tray & Toast Notifications](file:///e:/proooo/AUTO%20JOB/docs/TRAY_AND_NOTIFICATIONS.md)
- [Packaging & Binary Distribution](file:///e:/proooo/AUTO%20JOB/docs/PACKAGING.md)
- [Desktop Security & Local Isolation](file:///e:/proooo/AUTO%20JOB/docs/DESKTOP_SECURITY.md)
- [Design System Specification](file:///e:/proooo/AUTO%20JOB/docs/DESIGN_SYSTEM.md)
- [Component Library Reference](file:///e:/proooo/AUTO%20JOB/docs/COMPONENT_LIBRARY.md)
- [Accessibility & WCAG 2.2 Compliance](file:///e:/proooo/AUTO%20JOB/docs/ACCESSIBILITY.md)
- [UI Design Tokens Reference](file:///e:/proooo/AUTO%20JOB/docs/UI_TOKENS.md)
- [Frontend Layout Architecture](file:///e:/proooo/AUTO%20JOB/docs/FRONTEND_LAYOUTS.md)
- [Navigation Architecture](file:///e:/proooo/AUTO%20JOB/docs/NAVIGATION_ARCHITECTURE.md)
- [Expandable & Collapsible Sidebar Design](file:///e:/proooo/AUTO%20JOB/docs/SIDEBAR_DESIGN.md)
- [Navigation Accessibility & Shortcuts](file:///e:/proooo/AUTO%20JOB/docs/NAVIGATION_ACCESSIBILITY.md)
- [Navigation Test & Verification Report](file:///e:/proooo/AUTO%20JOB/docs/NAVIGATION_TESTING.md)
- [Command Center Dashboard](file:///e:/proooo/AUTO%20JOB/docs/COMMAND_CENTER.md)
- [Dashboard Data Contracts](file:///e:/proooo/AUTO%20JOB/docs/DASHBOARD_DATA_CONTRACTS.md)
- [Dashboard Metrics & Calculation Rules](file:///e:/proooo/AUTO%20JOB/docs/DASHBOARD_METRICS.md)
- [Real-Time SSE Event Streaming & Deduplication](file:///e:/proooo/AUTO%20JOB/docs/DASHBOARD_EVENTS.md)
- [Dashboard Automated Testing Report](file:///e:/proooo/AUTO%20JOB/docs/DASHBOARD_TESTING.md)
- [Module Architecture & Workspace Layout](file:///e:/proooo/AUTO%20JOB/docs/MODULE_ARCHITECTURE.md)
- [Workspace Navigation & Route Integration](file:///e:/proooo/AUTO%20JOB/docs/WORKSPACE_NAVIGATION.md)
- [Module Capabilities & Roadmap Activation Matrix](file:///e:/proooo/AUTO%20JOB/docs/MODULE_CAPABILITIES.md)
- [Module Data Contracts & REST APIs](file:///e:/proooo/AUTO%20JOB/docs/MODULE_DATA_CONTRACTS.md)
- [Cross-Module Autonomous Workflows](file:///e:/proooo/AUTO%20JOB/docs/CROSS_MODULE_WORKFLOWS.md)
- [Module Automated Testing Report](file:///e:/proooo/AUTO%20JOB/docs/MODULE_TESTING.md)
- [Settings & Operational Controls Architecture](file:///e:/proooo/AUTO%20JOB/docs/SETTINGS_ARCHITECTURE.md)
- [Settings Data Contracts & Schema Specification](file:///e:/proooo/AUTO%20JOB/docs/SETTINGS_SCHEMA.md)
- [AI Provider Configuration & VRAM Resource Management](file:///e:/proooo/AUTO%20JOB/docs/AI_PROVIDER_CONFIGURATION.md)
- [Agent Preferences & Directory Configuration](file:///e:/proooo/AUTO%20JOB/docs/AGENT_CONFIGURATION.md)
- [Automation Controls & Worker Pool Management](file:///e:/proooo/AUTO%20JOB/docs/AUTOMATION_CONTROLS.md)
- [Action Permissions & Killswitch Architecture](file:///e:/proooo/AUTO%20JOB/docs/PERMISSIONS_UI.md)
- [Settings Automated Testing & Verification Matrix](file:///e:/proooo/AUTO%20JOB/docs/SETTINGS_TESTING.md)
- [AI Model Gateway Specification](file:///e:/proooo/AUTO%20JOB/docs/AI_GATEWAY.md)
- [AI Provider Integrations](file:///e:/proooo/AUTO%20JOB/docs/AI_PROVIDERS.md)
- [Intelligent Model Routing](file:///e:/proooo/AUTO%20JOB/docs/MODEL_ROUTING.md)
- [Local Model & Hardware Optimization](file:///e:/proooo/AUTO%20JOB/docs/LOCAL_MODEL_MANAGEMENT.md)
- [AI Context Budgeting & Token Management](file:///e:/proooo/AUTO%20JOB/docs/AI_CONTEXT_MANAGEMENT.md)
- [AI Usage Accounting & Cost Tracking](file:///e:/proooo/AUTO%20JOB/docs/AI_USAGE_AND_COSTS.md)
- [AI Privacy & Security Architecture](file:///e:/proooo/AUTO%20JOB/docs/AI_PRIVACY.md)
- [AI Streaming Architecture](file:///e:/proooo/AUTO%20JOB/docs/AI_STREAMING.md)
- [AI Gateway Testing & Verification](file:///e:/proooo/AUTO%20JOB/docs/AI_TESTING.md)
- [Multi-Agent Architecture](file:///e:/proooo/AUTO%20JOB/docs/MULTI_AGENT_ARCHITECTURE.md)
- [Supervisor Agent Specification](file:///e:/proooo/AUTO%20JOB/docs/SUPERVISOR_AGENT.md)
- [Planning Engine & Goal Decomposition](file:///e:/proooo/AUTO%20JOB/docs/PLANNING_ENGINE.md)
- [Task Routing & Capability Matching](file:///e:/proooo/AUTO%20JOB/docs/AGENT_ROUTING.md)
- [Workflow DAG Engine](file:///e:/proooo/AUTO%20JOB/docs/WORKFLOW_DAG.md)
- [Agent Communication & Event Ledger](file:///e:/proooo/AUTO%20JOB/docs/AGENT_COMMUNICATION.md)
- [Verification Agent Architecture](file:///e:/proooo/AUTO%20JOB/docs/AGENT_VERIFICATION.md)
- [Recovery Agent & Fault Remediation](file:///e:/proooo/AUTO%20JOB/docs/AGENT_RECOVERY.md)
- [Orchestration Security & Governance](file:///e:/proooo/AUTO%20JOB/docs/ORCHESTRATION_SECURITY.md)
- [Orchestration Testing & Verification Guide](file:///e:/proooo/AUTO%20JOB/docs/ORCHESTRATION_TESTING.md)
- [Specialist AI Agent Framework](file:///e:/proooo/AUTO%20JOB/docs/SPECIALIST_AGENT_FRAMEWORK.md)
- [Specialist AI Agent Catalog](file:///e:/proooo/AUTO%20JOB/docs/SPECIALIST_AGENT_CATALOG.md)
- [Agent Manifest Specification](file:///e:/proooo/AUTO%20JOB/docs/AGENT_MANIFESTS.md)
- [Agent Model Profiles & Hardware Optimization](file:///e:/proooo/AUTO%20JOB/docs/AGENT_MODEL_PROFILES.md)
- [Recruitment Specialist Agents](file:///e:/proooo/AUTO%20JOB/docs/RECRUITMENT_AGENTS.md)
- [Computer & OS Operation Agents](file:///e:/proooo/AUTO%20JOB/docs/COMPUTER_AGENTS.md)
- [Productivity Specialist Agents](file:///e:/proooo/AUTO%20JOB/docs/PRODUCTIVITY_AGENTS.md)
- [Creative, Comms, Coding, & Automation Agents](file:///e:/proooo/AUTO%20JOB/docs/CREATIVE_AND_COMMUNICATION_AGENTS.md)
- [Agent Security & Context Isolation](file:///e:/proooo/AUTO%20JOB/docs/AGENT_SECURITY.md)
- [Agent Testing & Verification Guide](file:///e:/proooo/AUTO%20JOB/docs/AGENT_TESTING.md)
- [Authorization Engine Architecture](file:///e:/proooo/AUTO%20JOB/docs/AUTHORIZATION_ENGINE.md)
- [Permission & Risk Taxonomy Model](file:///e:/proooo/AUTO%20JOB/docs/PERMISSION_MODEL.md)
- [Authorization Policy Schema & Baselines](file:///e:/proooo/AUTO%20JOB/docs/POLICY_SCHEMA.md)
- [Preauthorized Autonomy & Standing Grants](file:///e:/proooo/AUTO%20JOB/docs/AUTONOMOUS_GRANTS.md)
- [Human-in-the-Loop Approval Workflows](file:///e:/proooo/AUTO%20JOB/docs/APPROVAL_WORKFLOWS.md)
- [Secure Tool Execution Gateway](file:///e:/proooo/AUTO%20JOB/docs/TOOL_EXECUTION_SECURITY.md)
- [Global Emergency Stop & Automation Pause](file:///e:/proooo/AUTO%20JOB/docs/EMERGENCY_STOP.md)
- [Recruitment Authorization Governance](file:///e:/proooo/AUTO%20JOB/docs/RECRUITMENT_AUTHORIZATION.md)
- [Security & Authorization Audit Ledger](file:///e:/proooo/AUTO%20JOB/docs/SECURITY_AUDIT.md)
- [Prompt Injection & Adversarial Attack Defenses](file:///e:/proooo/AUTO%20JOB/docs/PROMPT_INJECTION_DEFENSES.md)
- [Stage 14 Authorization Testing & Verification](file:///e:/proooo/AUTO%20JOB/docs/AUTHORIZATION_TESTING.md)
- [Persistent Memory Engine Architecture](file:///e:/proooo/AUTO%20JOB/docs/MEMORY_ARCHITECTURE.md)
- [Cognitive Memory Types (Episodic, Semantic, Procedural, Working)](file:///e:/proooo/AUTO%20JOB/docs/MEMORY_TYPES.md)
- [Memory Schema, Scopes, and Provenance](file:///e:/proooo/AUTO%20JOB/docs/MEMORY_SCHEMA.md)
- [Local Embedding Engine & Data Egress Guardrails](file:///e:/proooo/AUTO%20JOB/docs/EMBEDDING_ARCHITECTURE.md)
- [SQLite & In-Memory Vector Storage](file:///e:/proooo/AUTO%20JOB/docs/VECTOR_STORAGE.md)
- [Hybrid Retrieval (FTS5 + Dense Vectors + RRF)](file:///e:/proooo/AUTO%20JOB/docs/HYBRID_RETRIEVAL.md)
- [Context Engineering & Prompt Token Budgeting](file:///e:/proooo/AUTO%20JOB/docs/CONTEXT_ENGINEERING.md)
- [Memory Consolidation & Procedural Extraction](file:///e:/proooo/AUTO%20JOB/docs/MEMORY_CONSOLIDATION.md)
- [Memory Security, Scope Isolation, and Prompt Injection Defense](file:///e:/proooo/AUTO%20JOB/docs/MEMORY_SECURITY.md)
- [Memory Lifecycle, Retention, and Secure Deletion](file:///e:/proooo/AUTO%20JOB/docs/MEMORY_LIFECYCLE.md)
- [Memory Quality Evaluation Benchmark](file:///e:/proooo/AUTO%20JOB/docs/MEMORY_EVALUATION.md)
- [Stage 15 Memory Testing & Verification Matrix](file:///e:/proooo/AUTO%20JOB/docs/MEMORY_TESTING.md)
- [Browser Automation Architecture](file:///e:/proooo/AUTO%20JOB/docs/BROWSER_AUTOMATION_ARCHITECTURE.md)
- [Browser Runtime & Engine Discovery](file:///e:/proooo/AUTO%20JOB/docs/BROWSER_RUNTIME.md)
- [Browser Session & Tab Management](file:///e:/proooo/AUTO%20JOB/docs/BROWSER_SESSIONS.md)
- [Browser Authentication & DPAPI Encrypted Profiles](file:///e:/proooo/AUTO%20JOB/docs/BROWSER_AUTHENTICATION.md)
- [DOM Interaction & Form Analysis](file:///e:/proooo/AUTO%20JOB/docs/DOM_INTERACTION.md)
- [Browser Tool Contracts & API Endpoints](file:///e:/proooo/AUTO%20JOB/docs/BROWSER_TOOL_CONTRACTS.md)
- [Browser Security & Origin Controls](file:///e:/proooo/AUTO%20JOB/docs/BROWSER_SECURITY.md)
- [Browser Downloads & Artifact Storage](file:///e:/proooo/AUTO%20JOB/docs/BROWSER_DOWNLOADS.md)
- [Browser Execution Recovery & Self-Healing](file:///e:/proooo/AUTO%20JOB/docs/BROWSER_RECOVERY.md)
- [Multi-Agent Browser Integration](file:///e:/proooo/AUTO%20JOB/docs/BROWSER_AGENT_INTEGRATION.md)
- [Stage 16 Browser Testing & Verification](file:///e:/proooo/AUTO%20JOB/docs/BROWSER_TESTING.md)
- [Windows Structural Automation Architecture](file:///e:/proooo/AUTO%20JOB/docs/WINDOWS_AUTOMATION_ARCHITECTURE.md)
- [UI Automation Engine Specification](file:///e:/proooo/AUTO%20JOB/docs/UI_AUTOMATION_ENGINE.md)
- [UIA COM Threading & Concurrency](file:///e:/proooo/AUTO%20JOB/docs/UIA_COM_THREADING.md)
- [Window Discovery & Lifetime Tracking](file:///e:/proooo/AUTO%20JOB/docs/WINDOW_DISCOVERY.md)
- [Accessibility Tree Inspection & Serialization](file:///e:/proooo/AUTO%20JOB/docs/ACCESSIBILITY_TREE_INSPECTION.md)
- [Desktop Action Contracts & Execution](file:///e:/proooo/AUTO%20JOB/docs/DESKTOP_ACTION_CONTRACTS.md)
- [Windows Automation Security & Guardrails](file:///e:/proooo/AUTO%20JOB/docs/WINDOWS_AUTOMATION_SECURITY.md)
- [Desktop Failure Recovery & Self-Healing](file:///e:/proooo/AUTO%20JOB/docs/DESKTOP_RECOVERY.md)
- [Multi-Agent Computer Control Integration](file:///e:/proooo/AUTO%20JOB/docs/COMPUTER_AGENT_INTEGRATION.md)
- [Stage 17 Windows Automation Testing Report](file:///e:/proooo/AUTO%20JOB/docs/WINDOWS_AUTOMATION_TESTING.md)
- [Visual Automation Architecture](file:///e:/proooo/AUTO%20JOB/docs/VISUAL_AUTOMATION_ARCHITECTURE.md)
- [Windows Capture Engine & Providers](file:///e:/proooo/AUTO%20JOB/docs/WINDOWS_CAPTURE_ENGINE.md)
- [Capture Session Management](file:///e:/proooo/AUTO%20JOB/docs/CAPTURE_SESSION_MANAGEMENT.md)
- [Visual Coordinate Systems & Transformations](file:///e:/proooo/AUTO%20JOB/docs/VISUAL_COORDINATE_SYSTEM.md)
- [Vision-Language Model Integration](file:///e:/proooo/AUTO%20JOB/docs/VISION_MODEL_INTEGRATION.md)
- [Visual UI Grounding & Disambiguation](file:///e:/proooo/AUTO%20JOB/docs/VISUAL_GROUNDING.md)
- [Windows Visual Input Dispatch](file:///e:/proooo/AUTO%20JOB/docs/WINDOWS_VISUAL_INPUT.md)
- [Visual Action Verification & Transitions](file:///e:/proooo/AUTO%20JOB/docs/VISUAL_VERIFICATION.md)
- [Visual Automation Security & Guardrails](file:///e:/proooo/AUTO%20JOB/docs/VISUAL_AUTOMATION_SECURITY.md)
- [Visual Resource Management & Protection](file:///e:/proooo/AUTO%20JOB/docs/VISUAL_RESOURCE_MANAGEMENT.md)
- [Visual Agent Integration & Capabilities](file:///e:/proooo/AUTO%20JOB/docs/VISUAL_AGENT_INTEGRATION.md)
- [Stage 18 Visual Automation Testing Report](file:///e:/proooo/AUTO%20JOB/docs/VISUAL_AUTOMATION_TESTING.md)
- [Hybrid Computer Interaction Architecture](file:///e:/proooo/AUTO%20JOB/docs/HYBRID_COMPUTER_ARCHITECTURE.md)
- [Interaction Adapters Specification](file:///e:/proooo/AUTO%20JOB/docs/INTERACTION_ADAPTERS.md)
- [Unified Target Identity & Surface Classification](file:///e:/proooo/AUTO%20JOB/docs/HYBRID_TARGET_IDENTITY.md)
- [Dynamic Control Routing Engine](file:///e:/proooo/AUTO%20JOB/docs/HYBRID_ROUTING.md)
- [Context-Aware Fallback & Recovery Engine](file:///e:/proooo/AUTO%20JOB/docs/HYBRID_FALLBACK.md)
- [Cross-Method Observation & Unified Perception](file:///e:/proooo/AUTO%20JOB/docs/HYBRID_OBSERVATION.md)
- [Unified Action Contracts & Execution Lifecycle](file:///e:/proooo/AUTO%20JOB/docs/HYBRID_ACTION_CONTRACTS.md)
- [Hybrid Engine Security & Session Guards](file:///e:/proooo/AUTO%20JOB/docs/HYBRID_SECURITY.md)
- [Hardware & Resource-Conscious Interaction](file:///e:/proooo/AUTO%20JOB/docs/HYBRID_RESOURCE_MANAGEMENT.md)
- [Multi-Agent Coordination & Hybrid Capabilities](file:///e:/proooo/AUTO%20JOB/docs/HYBRID_AGENT_INTEGRATION.md)
- [Stage 19 Hybrid Engine Testing & Verification Report](file:///e:/proooo/AUTO%20JOB/docs/HYBRID_TESTING.md)
- [Action Recording Architecture](file:///e:/proooo/AUTO%20JOB/docs/ACTION_RECORDING_ARCHITECTURE.md)
- [Recording Privacy & Sensitive Data Protection](file:///e:/proooo/AUTO%20JOB/docs/RECORDING_PRIVACY.md)
- [Reusable Procedure Specification & Schema](file:///e:/proooo/AUTO%20JOB/docs/PROCEDURE_SCHEMA.md)
- [Procedure Compilation Pipeline](file:///e:/proooo/AUTO%20JOB/docs/PROCEDURE_COMPILATION.md)
- [Procedure Replay & Execution Engine](file:///e:/proooo/AUTO%20JOB/docs/PROCEDURE_EXECUTION.md)
- [Checkpoint Architecture & Integrity Verification](file:///e:/proooo/AUTO%20JOB/docs/CHECKPOINT_ARCHITECTURE.md)
- [External Side-Effects & Idempotency Ledger](file:///e:/proooo/AUTO%20JOB/docs/EXTERNAL_SIDE_EFFECTS.md)
- [Autonomous Computer Crash Recovery & Resume Planning](file:///e:/proooo/AUTO%20JOB/docs/COMPUTER_RECOVERY.md)
- [Procedure Security & Authorization Governance](file:///e:/proooo/AUTO%20JOB/docs/PROCEDURE_SECURITY.md)
- [Procedure Agent Integration & Multi-Agent Coordination](file:///e:/proooo/AUTO%20JOB/docs/PROCEDURE_AGENT_INTEGRATION.md)
- [Stage 20 Computer Workflow Testing & Verification Report](file:///e:/proooo/AUTO%20JOB/docs/COMPUTER_WORKFLOW_TESTING.md)
- [Stage Progress Log](file:///e:/proooo/AUTO%20JOB/docs/STAGE_LOG.md)

## Development Setup

### Automated Quick Setup (Windows 11)

```powershell
.\scripts\setup.ps1
```

### Launch Development Environment

```powershell
.\scripts\dev.ps1
```

### Run Full-Stack Tests

```powershell
.\scripts\test.ps1
```

### Run Quality & Validation Checks

```powershell
.\scripts\check.ps1
```

### Database & Storage Operations

```powershell
.\scripts\db-status.ps1     # Inspect database metrics and schema version
.\scripts\db-verify.ps1     # Execute PRAGMA integrity and foreign key checks
.\scripts\db-backup.ps1     # Create consistent online backup with SHA-256 manifest
.\scripts\db-restore.ps1    # Restore database with safety snapshot
.\scripts\db-migrate.ps1    # Apply pending Alembic migrations
```

### Build & Packaging (Stage 05)

```powershell
.\scripts\package-backend.ps1   # Package Python backend into frozen standalone binary
.\scripts\package-desktop.ps1   # Full build: frontend + backend sidecar + release Tauri desktop exe
.\scripts\verify-package.ps1    # Automated package verification & live health probe
```

### Build Production Artifacts

```powershell
.\scripts\build.ps1
```
