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

### Build Production Artifacts

```powershell
.\scripts\build.ps1
```
