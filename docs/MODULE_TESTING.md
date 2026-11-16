# AUTONOM — Module Testing Strategy & Test Execution (Stage 09)

## 1. Overview

Testing for Stage 09 encompasses both backend REST API validation (FastAPI + SQLAlchemy async + SQLite) and desktop frontend UI/route integration (Vitest + React Testing Library + JSDOM).

---

## 2. Test Suites

### A. Backend Pytest Suites (`services/api/tests/`)

- `test_api_jobs_apps_artifacts.py`: 10 integration tests validating `GET /jobs`, `GET /jobs/{id}`, `GET /applications`, `GET /applications/{id}`, `GET /artifacts`, and `GET /artifacts/{id}` with unauthenticated rejection, 404 handling, pagination, and genuine SQLite database records.
- Total Backend Tests: **57 passed** across all test suites.

To run:

```powershell
services\api\.venv\Scripts\python.exe -m pytest services\api\tests -q
```

### B. Desktop Vitest Suites (`apps/desktop/src/test/`)

- `module/module-components.test.tsx`: Validates shared primitives (`ModulePage`, `ModuleHeader`, `ModuleToolbar`, `ModuleTabs`, `ModuleEmptyState`, `ModuleUnavailableState`, `ModuleErrorState`, `ModuleDetailPanel`).
- `features/agents-workspace.test.tsx`: Validates 24-agent catalog, category filtering, search, worker pool status, and slide-over inspector.
- `features/recruitment-workspace.test.tsx`: Validates genuine job listing cards, 10-stage pipeline, and detail drawer.
- `features/computer-workspace.test.tsx`: Validates dual-modality perception status and hardware killswitch hotkey attribution.
- `features/workflows-workspace.test.tsx`: Validates durable task queues, progress bars, cancellation, and diagnostic task dispatch.
- `features/documents-workspace.test.tsx`: Validates artifact metadata, file size formatting, and SHA-256 checksums.
- `features/activity-workspace.test.tsx`: Validates immutable event ledger, state transitions, and JSON payload viewer.
- `features/navigation-integration.test.tsx`: Validates cross-module lazy-loaded route rendering and `Suspense` fallbacks.
- `App.test.tsx`: End-to-end routing and cross-module navigation from sidebar.
- Total Desktop Tests: **90 passed** across 26 test files.

To run:

```powershell
pnpm.cmd --filter @autonom/desktop test
```

### C. Type Checking & Bundle Verification

```powershell
pnpm.cmd --filter @autonom/desktop typecheck
pnpm.cmd --filter @autonom/desktop build
```

Both commands exit cleanly with code `0`.
