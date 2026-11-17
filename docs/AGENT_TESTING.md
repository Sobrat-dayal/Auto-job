# AUTONOM — Agent Testing, Verification, & Quality Assurance

## 1. Testing Strategy

Testing the Specialist AI Agent Framework requires a multi-tiered approach:
1. **Manifest & Invariant Unit Tests**: Validates that schemas, model profiles, context policies, and security invariants hold true across all 24 agents.
2. **Specialist Capability Tests**: Verifies that each of the 32 specialist capability handlers correctly processes inputs, handles edge cases, and produces validated outputs.
3. **End-to-End Collaboration Tests**: Verifies multi-agent DAG pipelines orchestrating real handoffs between specialist agents (e.g., Job Analysis -> Skill Matching -> Resume Tailoring -> Verifier).
4. **Resilience & Security Tests**: Asserts context isolation (credential rejection), agent deactivation, recovery handling on failed contracts, and persistent telemetry tracking.
5. **Frontend Workspace Integration Tests**: Asserts full React component rendering, category filtering, manifest loading, configuration editing, and live diagnostic execution.

---

## 2. Automated Test Inventory

### 2.1 Backend Pytest Suite

| Test File | Test Case | Target Agent / Subsystem | Outcome |
|---|---|---|---|
| `test_specialist_agents.py` | `test_agent_manifest_validation` | `validate_manifest`, Security invariant | Passed |
| `test_specialist_agents.py` | `test_agent_catalog_registration` | `AgentRegistry`, 24 default agents | Passed |
| `test_specialist_agents.py` | `test_specialist_capability_execution` | All specialist classes & capabilities | Passed |
| `test_specialist_agents.py` | `test_live_recruitment_multi_agent_workflow` | Recruitment 4-agent DAG pipeline | Passed |
| `test_specialist_agents.py` | `test_live_coding_technical_review_workflow` | Coding & Review 3-agent DAG pipeline | Passed |
| `test_specialist_agents.py` | `test_agent_api_endpoints` | REST API endpoints (GET, PATCH, POST) | Passed |
| `test_specialist_collaboration.py` | `test_context_isolation_credential_rejection` | Context isolation & sensitive key rejection | Passed |
| `test_specialist_collaboration.py` | `test_disabled_agent_behavior` | Active state toggles & deactivation | Passed |
| `test_specialist_collaboration.py` | `test_controlled_failure_recovery_and_persistence` | RecoveryAgent triage & DAG replanning | Passed |
| `test_specialist_collaboration.py` | `test_agent_execution_history_persistence` | SQLite telemetry & execution tracking | Passed |

### 2.2 Frontend Vitest Suite (`apps/desktop/src/test/features/agents-workspace.test.tsx`)

| Test Case | Description | Outcome |
|---|---|---|
| `renders agents workspace heading and category filter` | Verifies header, category filter pills, and agent counts | Passed |
| `renders agent cards with status and capabilities` | Verifies card rendering, availability badges, and capability tags | Passed |
| `filters agents by category` | Verifies switching from All to Recruitment filters list accurately | Passed |
| `opens detail inspector when clicking an agent card` | Verifies side drawer inspection with Overview, Config, History, Diagnostics | Passed |
| `runs diagnostic check on selected agent` | Verifies live diagnostic API call and success banner display | Passed |

---

## 3. Running the Test Suites

### Backend Tests
```bash
# Set PYTHONPATH to services/api and invoke pytest with the virtual environment Python
$env:PYTHONPATH="services/api"
& "services/api/.venv/Scripts/python.exe" -m pytest services/api/tests/ -v
```

### Frontend Tests
```bash
npm.cmd run test
```

### Production Monorepo Build Check
```bash
npm.cmd run build
```
