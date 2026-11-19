# Recruitment Monitoring Testing & Verification (Stage 30)

## 1. Test Suite Architecture
Stage 30 verification incorporates 43 comprehensive unit, property, and integration tests across 8 test suites:

1. **`test_recruitment_monitoring_schedules.py`** (11 tests):
   - Timezone-aware recurrence math (intervals, hourly, daily, weekdays, weekly).
   - Enforces 5-minute minimum interval via Pydantic validation.
   - Missed run policy evaluation (`skip`, `run_latest_due`, `require_review`).
   - Schedule preview generator with quiet hours detection and request budget estimation.
2. **`test_quiet_hours_and_power.py`** (5 tests):
   - Cross-midnight quiet hours evaluation (e.g. 22:00 to 08:00).
   - Notification muting vs source monitoring pause behavior.
   - Timezone offset conversion (e.g. Eastern Time to UTC).
   - Windows lifecycle settings retrieval and patch updates.
3. **`test_worker_leases_and_budgets.py`** (5 tests):
   - SQLite worker lease acquisition, heartbeats, and conflict prevention.
   - Reclaiming expired leases based on TTL.
   - Budget controller concurrency limits ($N \le 3$).
   - Daily request quota enforcement ($M \le 500$ requests/day).
   - Provider rate-limit cooldown tracking and remaining seconds calculation.
4. **`test_job_change_detection.py`** (6 tests):
   - HTML stripping, whitespace collapsing, and SHA-256 semantic content hashing.
   - Material requirement updates vs formatting-only changes.
   - Detection of new vacancies, closures, reopenings, salary shifts, location changes, and remote condition adjustments.
5. **`test_opportunity_queue_readiness.py`** (4 tests):
   - Evaluation of Stage 31 preparation readiness (`OpportunityPreparationCandidate`).
   - Blocking gaps preventing preparation handoff.
   - Closed vacancies preventing readiness handoff.
   - Opportunity queue upserting, priority scoring, user actions (`save`, `prioritize`, `exclude`), and history logging.
6. **`test_alerts_and_outbox.py`** (4 tests):
   - Alert rule lifecycle and condition filtering.
   - Alert emission, fingerprinting, and cooldown deduplication.
   - Alert acknowledgement and dismissal.
   - Outbox processing and quiet hours deferral.
7. **`test_emergency_stop_monitoring.py`** (2 tests):
   - Emergency stop activation blocking monitoring runs.
   - Automation pause state blocking scheduled runs.
8. **`test_api_recruitment_monitoring.py`** (6 tests):
   - Local authentication enforcement (401 without bearer token).
   - Overview KPI endpoint (`/status`).
   - Full watch lifecycle CRUD, preview, pause, resume, and deletion (`/watches`).
   - Monitoring runs, opportunities, and changes listing endpoints.
   - Diagnostics report and alert management endpoints.
   - Windows background monitoring settings endpoints.

## 2. Test Execution Evidence
- **Backend Pytest Suite**: 43 passed in 6.43s (100% pass rate).
- **Matching Regression Tests**: 4 passed in 1.50s (100% pass rate).
- **Frontend Vitest Suite**: 46 test files passed, 202 tests passed in 29.09s (100% pass rate).
- **Desktop Typecheck**: 0 errors.
