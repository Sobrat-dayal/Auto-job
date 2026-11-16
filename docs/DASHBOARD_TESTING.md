# AUTONOM — Dashboard Automated Testing & Verification (Stage 08)

## 1. Testing Strategy

The Command Center dashboard is validated through automated tests spanning:

1. **Backend Integration Tests (Pytest)**: Fast API contract validation, endpoint authentication, state computation, error simulation.
2. **Frontend Component & Unit Tests (Vitest + Testing Library)**: UI rendering, loading states, roadmap attribution tags, event stream handling, filtering, modal inspection.
3. **TypeScript Strict Typechecking**: Full static compilation (`tsc && vite build`) with zero type errors.

---

## 2. Test Execution Summary

### 2.1 Backend Pytest Suite

Executed via:

```powershell
& "services/api/.venv/Scripts/python.exe" -m pytest services/api/tests
```

#### Results

- **Total Tests**: 47 passed in 3.65s.
- **Dashboard Test Suite**: `services/api/tests/test_api_dashboard.py` (4 integration tests):
  - `test_dashboard_overview_unauthenticated`: Verifies 401 Unauthorized without Bearer token.
  - `test_dashboard_overview_authenticated`: Validates `DashboardOverviewResponse` schema, SQLite task counts, 3 agent statuses, worker capacity.
  - `test_dashboard_task_trends`: Tests time-bucketing (`today`, `7d`, `30d`), overall success rate computation, and total volume aggregates.
  - `test_dashboard_activity`: Tests durable event stream retrieval from `task_events` table.

---

### 2.2 Frontend Vitest Suite

Executed via:

```powershell
pnpm --filter @autonom/desktop test
```

#### Results

- **Test Files**: 18 passed (18 total).
- **Tests**: 65 passed (65 total).
- **Duration**: ~15s.

#### Stage 08 Dashboard Test Suites

1. **`dashboard-kpi.test.tsx` (4 tests)**:
   - Renders loading skeleton placeholders when loading without data.
   - Renders primary KPI cards with honest values and roadmap badges (`Stage 26`, `Stage 31`).
   - Renders secondary operational metrics (Completed, Failed, Pending Approvals `Stage 14`, Worker Threads).
   - Invokes filter callback when clicking on task KPI cards.
2. **`dashboard-agents.test.tsx` (3 tests)**:
   - Renders 3 prominent agent cards with honest `UNAVAILABLE` badges and roadmap release tags (`Stage 26`, `Stage 30`, `Stage 12`).
   - Renders the 4th distinct card for real background worker threads (Stage 03 Active).
   - Triggers inspect agent callback when clicking info button.
3. **`dashboard-tasks.test.tsx` (4 tests)**:
   - Renders task queue table with all tasks and filter tab counts.
   - Filters tasks when selecting state tabs (`Running`, `Queued`, `Completed`, `Failed`).
   - Opens task details dialog when clicking inspect button.
   - Allows cooperative cancellation for running or queued tasks.
4. **`dashboard-activity.test.tsx` (3 tests)**:
   - Renders live activity feed events with stream status pill (`LIVE SSE (8765)`).
   - Filters events by category tabs (`all`, `tasks`, `workers`, `system`).
   - Invokes clear callback when clear button is clicked.
5. **`dashboard-pipeline.test.tsx` (5 tests)**:
   - Renders 10-stage application pipeline with counts.
   - Displays honest roadmap notice when applications count is zero (`Scheduled Stage 31`).
   - Navigates to applications page when clicking view kanban board.
   - Renders job discovery counts and active listings.
   - Displays honest roadmap attribution when jobs count is zero (`Stage 26`).

---

### 2.3 Production Build Verification

Executed via:

```powershell
pnpm --filter @autonom/desktop build
```

- **TypeScript**: 0 errors.
- **Vite Bundler**: Transformed 2367 modules successfully in 6.42s.
