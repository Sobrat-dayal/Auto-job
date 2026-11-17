# AUTONOM Memory Test Suite Matrix (Stage 15)

## 1. Test Coverage Overview

Stage 15 includes 17 dedicated automated tests spanning unit logic, security boundaries, workflow integrations, quality benchmarks, and desktop user interface components:

### Backend Python Pytest Suite (`services/api/tests/`)
1. `test_memory_service.py`:
   - `test_embedding_engine_properties`: Validates 384-dimensional unit vector generation, normalization, and cosine similarity.
   - `test_memory_write_and_deduplication`: Verifies SHA-256 checksum deduplication in identical scopes.
   - `test_hybrid_and_keyword_retrieval`: Validates RRF ranking, vector score, and FTS5 keyword recall.
   - `test_context_builder_budgeting`: Verifies structured section layout and token limit enforcement.
   - `test_conflict_detection_and_supersession`: Validates contradiction detection and superseding older records.
   - `test_memory_expiration_and_deletion`: Verifies retention sweeps and cascading index eviction.
2. `test_memory_security.py`:
   - `test_scope_isolation_scope_a_vs_scope_b`: Confirms Scope A queries cannot access Scope B records.
   - `test_prompt_injection_in_memory_treated_as_passive_evidence`: Confirms malicious injections in stored text cannot elevate permissions.
   - `test_data_egress_blocking_for_sensitive_categories`: Validates blocking of cloud models for sensitive records.
3. `test_memory_workflows.py`:
   - `test_recruitment_memory_workflow`: Section 58 workflow test verifying recruitment skill matching, preference updating, and supersession.
   - `test_experience_memory_and_procedure_extraction`: Section 59 workflow test verifying episodic outcome logging and procedure extraction.
4. `test_memory_evaluation.py`:
   - `test_retrieval_quality_evaluation`: Section 54 benchmark measuring MRR, Precision@K, and latency.

### Frontend Vitest Suite (`apps/desktop/src/test/features/memory-workspace.test.tsx`)
1. Overview dashboard rendering real storage and index telemetry.
2. Memory Explorer tab with filtering by memory type.
3. Semantic and hybrid search execution with score badges.
4. Procedural knowledge tab displaying steps and capability bindings.
5. Conflict review panel displaying contradictions with resolution buttons.

---

## 2. Test Execution Commands

```powershell
# Run backend memory tests
$env:PYTHONPATH="services/api"
services/api/.venv/Scripts/python.exe -m pytest services/api/tests/test_memory_service.py services/api/tests/test_memory_security.py services/api/tests/test_memory_workflows.py services/api/tests/test_memory_evaluation.py -v

# Run full backend test suite (125 tests)
services/api/.venv/Scripts/python.exe -m pytest services/api/tests/ -q

# Run frontend Vitest suite (126 tests)
npm.cmd --prefix apps/desktop test
```
