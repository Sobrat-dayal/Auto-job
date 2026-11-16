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
