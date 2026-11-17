"""End-to-End Workflow Tests for Stage 15: Recruitment Memory and Experience Memory."""

import pytest

from app.db.engine import get_db_session
from app.memory.contracts import (
    ConfidenceCategory,
    ContextBuildRequest,
    MemoryCreateRequest,
    MemoryScope,
    MemorySearchRequest,
    MemoryType,
    ProvenanceMetadata,
    SearchMode,
    SensitivityCategory,
    VerificationStatus,
)
from app.memory.integrations.specialists import specialist_memory
from app.memory.integrations.supervisor import supervisor_memory
from app.memory.lifecycle.conflicts import conflict_resolver
from app.memory.lifecycle.consolidation import memory_consolidator
from app.memory.service import memory_service
from app.memory.storage.repository import MemoryRepository
from app.memory.storage.vector_store import vector_store


@pytest.fixture(autouse=True)
def clean_memory_index():
    vector_store.clear()
    yield


@pytest.mark.asyncio
async def test_recruitment_memory_workflow():
    """Section 58 Required Workflow Test: Recruitment Memory Lifecycle.

    1. Store verified technical skills for an applicant profile.
    2. Store verified project descriptions.
    3. Store a job preference.
    4. Verify the Job Matching Agent retrieves authorized relevant facts.
    5. Compare against supplied job requirements.
    6. Correct an outdated preference and verify supersession.
    """
    applicant_id = "applicant_jane_doe_101"

    # Step 1: Store verified technical skills
    skill_rec = await memory_service.write_memory(
        MemoryCreateRequest(
            memory_type=MemoryType.SEMANTIC,
            title="Verified Technical Skills: Rust & Python",
            content="5 years of production Rust backend development, async Tokio, PyO3 bindings, and FastAPI.",
            summary="Rust and Python backend expertise",
            owner_scope=MemoryScope.APPLICANT_PROFILE,
            scope_id=applicant_id,
            source_type="verified_profile",
            source_ref="resume_doc_001",
            verification_status=VerificationStatus.VERIFIED,
            confidence_category=ConfidenceCategory.HIGH,
            sensitivity_category=SensitivityCategory.PERSONAL,
        )
    )
    assert skill_rec.id.startswith("mem_")

    # Step 2: Store verified project description
    project_rec = await memory_service.write_memory(
        MemoryCreateRequest(
            memory_type=MemoryType.SEMANTIC,
            title="Verified Project: High-Throughput Trading Engine",
            content="Engineered low-latency order matching engine handling 50,000 orders/sec in Rust with SQLite logging.",
            summary="Trading engine project",
            owner_scope=MemoryScope.APPLICANT_PROFILE,
            scope_id=applicant_id,
            source_type="verified_profile",
            source_ref="github_repo_verified",
            verification_status=VerificationStatus.VERIFIED,
            confidence_category=ConfidenceCategory.HIGH,
        )
    )
    assert project_rec.id.startswith("mem_")

    # Step 3: Store initial work preference
    pref_rec_v1 = await memory_service.write_memory(
        MemoryCreateRequest(
            memory_type=MemoryType.SEMANTIC,
            title="Job Preference: Location",
            content="Candidate prefers remote-first roles located in North America or hybrid roles in New York City.",
            summary="Remote NA or hybrid NYC",
            owner_scope=MemoryScope.APPLICANT_PROFILE,
            scope_id=applicant_id,
            source_type="user_statement",
            verification_status=VerificationStatus.USER_CONFIRMED,
        )
    )

    # Step 4: Allow Job Matching Agent to retrieve authorized relevant facts
    job_query = "Senior Rust Systems Engineer needed for distributed low-latency platform"
    facts = await specialist_memory.get_recruitment_facts(job_query, applicant_id=applicant_id)

    assert len(facts) >= 1
    titles = [f.title for f in facts]
    assert any("Rust" in t or "Trading" in t for t in titles)
    # Confirm evidence is marked verified
    assert any(f.verification_status in (VerificationStatus.VERIFIED, VerificationStatus.USER_CONFIRMED) for f in facts)

    # Step 5: User updates/corrects preference (e.g., relocation to Austin, TX)
    pref_rec_v2 = await memory_service.write_memory(
        MemoryCreateRequest(
            memory_type=MemoryType.SEMANTIC,
            title="Job Preference: Location",
            content="Updated preference: Relocated to Austin, Texas; prefers local Austin hybrid or 100% remote worldwide.",
            summary="Austin hybrid or remote worldwide",
            owner_scope=MemoryScope.APPLICANT_PROFILE,
            scope_id=applicant_id,
            source_type="user_statement",
            verification_status=VerificationStatus.USER_CONFIRMED,
        )
    )

    # Resolve conflict & supersede old preference
    async with get_db_session() as session:
        await conflict_resolver.supersede_memory(session, old_memory_id=pref_rec_v1.id, new_memory_id=pref_rec_v2.id)

    # Step 6: Verify future recruitment retrieval excludes superseded preference
    updated_facts = await specialist_memory.get_recruitment_facts("Location preferences", applicant_id=applicant_id)
    retrieved_ids = [f.memory_id for f in updated_facts]
    assert pref_rec_v1.id not in retrieved_ids, "Superseded preference v1 must not be retrieved"
    assert pref_rec_v2.id in retrieved_ids, "New preference v2 must be retrieved"


@pytest.mark.asyncio
async def test_experience_memory_and_procedure_extraction():
    """Section 59 Required Workflow Test: Experience Memory and Procedure Extraction.

    1. Record episodic memory of a workflow outcome.
    2. Extract a reusable procedure from verified workflow execution steps.
    3. Retrieve the procedure and verify it does not bypass permissions.
    """
    workflow_id = "wf_experience_test_99"

    # 1. Record workflow episodic memory
    await supervisor_memory.record_workflow_experience(
        workflow_id=workflow_id,
        goal="Parse complex PDF resume and extract structured contact details",
        success=True,
        lessons="PDF text layer required OCR fallback for scanned header section.",
    )

    # Verify episodic memory exists
    res = await memory_service.search_memory(
        MemorySearchRequest(
            query="PDF resume OCR fallback",
            search_mode=SearchMode.HYBRID,
            scope_id="default_user",
        )
    )
    assert len(res.results) >= 1
    assert "OCR fallback" in res.results[0].content_snippet

    # 2. Extract candidate procedural memory
    steps = [
        {"name": "Extract Raw Text", "capability_id": "pdf_extract_text", "parameters": {"mode": "fast"}},
        {"name": "OCR Fallback if Empty", "capability_id": "ocr_scan_image", "parameters": {"dpi": 300}},
        {"name": "Structure Entities", "capability_id": "structured_extract", "parameters": {"schema": "contact_info"}},
    ]

    async with get_db_session() as session:
        proc_id = await memory_consolidator.extract_procedure_from_workflow(
            session=session,
            workflow_id=workflow_id,
            procedure_name="Robust Document Text & OCR Extraction",
            capability_id="structured_extract",
            steps=steps,
        )
        assert proc_id is not None

        repo = MemoryRepository(session)
        proc = await repo.get_procedure(proc_id)
        assert proc is not None
        assert proc.name == "Robust Document Text & OCR Extraction"
        assert len(proc.steps_json) == 3
        # Confirm procedure declares required permissions
        assert "capability:structured_extract" in proc.required_permissions_json
