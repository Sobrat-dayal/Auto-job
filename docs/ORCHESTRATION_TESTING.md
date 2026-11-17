# Orchestration Testing & Verification Guide (Stage 12)

## 1. Test Overview

Stage 12 is verified across a comprehensive test matrix spanning Python backend unit/integration tests and React/TypeScript desktop frontend tests.

All tests run in automated CI and local developer environments.

---

## 2. Test Execution

### Backend Pytest Suite
Run the dedicated multi-agent orchestration test suite:
```bash
services/api/.venv/Scripts/python -m pytest services/api/tests/test_orchestration.py -v
```
Run the full backend test suite (84 tests):
```bash
services/api/.venv/Scripts/python -m pytest services/api/tests/ -v
```

### Desktop Vitest Suite
Run the orchestration frontend feature tests:
```powershell
npm.cmd test -- src/test/features/workflows-workspace.test.tsx src/test/features/agents-workspace.test.tsx
```
Run the full frontend test suite (110 tests):
```powershell
npm.cmd test
```

---

## 3. Test Coverage Matrix

1. `test_dependency_graph_topological_sort_and_stages`:
   - Validates Kahn's algorithm topological order.
   - Computes multi-level parallel stages.
   - Evaluates dynamic executable step resolution as dependencies complete.
2. `test_dependency_graph_cycle_detection`:
   - Validates fast failure when cyclic dependencies are introduced.
3. `test_capabilities_execution`:
   - Validates code inspection, text diff, markdown report formatting, and schema validation.
4. `test_context_binding_resolution`:
   - Validates nested mustache binding resolution (`{{step_x.field}}`, `{{input.field}}`).
5. `test_agent_registry`:
   - Validates 5 core active coordination agents and roadmap specialist catalog.
6. `test_recovery_classification`:
   - Tests failure mapping across all 13 error conditions.
7. `test_end_to_end_job_analysis_workflow`:
   - Executes real recruitment workflow ("Analyze supplied job description, extract technical skills, summarize responsibilities, identify experience requirements, and produce a structured report") end-to-end.
8. `test_fastapi_orchestration_endpoints`:
   - Tests `/api/v1/orchestration/workflows`, `/dag`, `/agents`, `/capabilities`, and `/stats`.
