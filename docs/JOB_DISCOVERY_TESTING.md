# Job Discovery Testing Suite and Verification (Stage 26)

## Testing Strategy
Stage 26 features a dual test harness verifying backend models, connectors, security boundaries, snapshot safety invariants, and desktop frontend views:

### 1. Backend Pytest Suites (`services/api/tests/`)
- `test_discovery_models.py`: Data contracts, manifests, provenance models, and status enums.
- `test_discovery_security.py`: SSRF validation blocking private subnets (127.0.0.1, 10.0.0.0/8, 169.254.169.254), HTML sanitization, and prompt injection disarming.
- `test_discovery_connectors.py`: Fixture parsing for Greenhouse, Lever, Ashby, USAJOBS, RSS/Atom, JSON feeds, and manual imports.
- `test_discovery_sync.py`: Initial fetch, change detection, and verification of the **Partial Snapshot Safety Invariant** (partial failures never close postings).
- `test_discovery_policy_prefilter.py`: Integration with Stage 25 career preference strategies and hard constraint rejections.
- `test_api_job_discovery.py`: End-to-end integration tests for all 24 FastAPI endpoints.
- `test_live_public_discovery.py`: Optional live public board discovery test (skips gracefully when isolated from internet).

### 2. Desktop Vitest Suites (`apps/desktop/src/test/features/`)
- `job-discovery.test.tsx`:
  - Renders workspace header and summary KPI metrics.
  - Navigates to Job Sources tab and inspects configured providers.
  - Navigates to Discovered Jobs tab and inspects vacancies.
  - Navigates to Single Job Import tab and verifies URL/manual switching.
  - Navigates to Tasks Monitor and inspects background executions.

## Running Tests
```bash
# Run backend pytest suite
services/api/.venv/Scripts/pytest services/api/tests/test_discovery_*.py services/api/tests/test_api_job_discovery.py -v

# Run desktop Vitest suite
pnpm.cmd --filter @autonom/desktop test src/test/features/job-discovery.test.tsx
```
