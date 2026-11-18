# AUTONOM Recruitment Policy Testing Verification

## Stage 25 of 50 — Test Coverage & QA Sign-Off

---

### Backend Test Coverage (Pytest)

The Stage 25 backend implementation is verified by 12 dedicated test suites containing 31 test cases (100% pass rate) alongside full regression verification of 380 total backend tests:

| Test Suite | Tests | Scope |
|---|---|---|
| `test_policy_models.py` | 3 | Pydantic contracts, validation invariants, enum serialization. |
| `test_role_preferences.py` | 3 | Role family mapping, seniority parsing, keyword triggers and exclusions. |
| `test_location_preferences.py` | 1 | Geographic filtering, remote/hybrid rules, excluded city vetoes. |
| `test_compensation_policies.py` | 2 | Unit annualization, currency comparisons, undisclosed salary modes. |
| `test_employer_restrictions.py` | 3 | Allowlist modes, blocked employers, brand token ambiguity detection. |
| `test_job_eligibility.py` | 5 | Deterministic education, experience, skill overlap, and work auth audits. |
| `test_policy_precedence.py` | 4 | 10-level precedence ladder, emergency stop, and soft ranking. |
| `test_autonomy_modes.py` | 2 | Mode 1-4 capabilities, standing grants, and human review queues. |
| `test_multi_agent_budget.py` | 2 | Two-phase atomic reservation, confirmation, release, and resets. |
| `test_policy_simulation.py` | 1 | Zero-side-effect sandbox simulation and explanation outputs. |
| `test_agent_policy_integration.py` | 1 | Agent policy snapshotting and action permission pre-flights. |
| `test_api_recruitment_policy.py` | 4 | Authenticated REST endpoints (strategies, activation, simulation, diagnostics). |

**Backend Total**: 31 / 31 Stage 25 tests passing (100%), 380 / 380 full suite passing (100%).

---

### Desktop Vitest Test Coverage

The desktop frontend implementation is verified by 9 tests in `apps/desktop/src/test/features/recruitment-policy.test.tsx` (100% pass rate):

- Workspace rendering with active strategy and overview cards.
- Recent policy decisions and audit trail display.
- Switching to Target Roles tab and displaying configured roles.
- Switching to Locations tab and showing work arrangement options.
- Switching to Compensation tab and verifying salary floor settings.
- Switching to Employers tab and showing blocked company items.
- Switching to Precedence tab and visualizing 10-level hierarchy.
- Switching to Budgets tab and displaying multi-agent limits.
- Running Policy Simulator and presenting explainable verdict breakdown.

**Frontend Total**: 9 / 9 Vitest tests passing (100%).
