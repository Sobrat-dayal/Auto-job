"""Unit tests for Stage 15 Memory Engine: creation, hybrid retrieval, deduplication, and lifecycle."""

from datetime import UTC, datetime, timedelta
import uuid
import pytest
import pytest_asyncio

from app.db.engine import get_db_session
from app.db.migrations import init_database_schema
from app.db.models import Base
from app.memory.contracts import (
    ContextBuildRequest,
    MemoryCreateRequest,
    MemoryScope,
    MemorySearchRequest,
    MemoryType,
    ProvenanceMetadata,
    RetentionPolicy,
    SearchMode,
    SensitivityCategory,
    VerificationStatus,
)
from app.memory.embeddings.provider import DeterministicLocalEmbeddingEngine
from app.memory.lifecycle.conflicts import conflict_resolver
from app.memory.lifecycle.deduplication import deduplication_service
from app.memory.lifecycle.expiration import expiration_manager
from app.memory.service import memory_service
from app.memory.storage.repository import MemoryRepository
from app.memory.storage.vector_store import vector_store


@pytest.fixture(autouse=True)
def clean_memory_index():
    """Clear in-memory vector index before each test."""
    vector_store.clear()
    yield


@pytest.mark.asyncio
async def test_embedding_engine_properties():
    """Verify deterministic embedding dimensions and cosine similarity normalization."""
    engine = DeterministicLocalEmbeddingEngine(dimension=384)
    v1 = await engine.embed_text("python fastapi rust developer")
    v2 = await engine.embed_text("python fastapi software engineer")
    v3 = await engine.embed_text("baking strawberry cheesecake in oven")

    assert len(v1) == 384
    assert len(v2) == 384
    assert len(v3) == 384

    # Dot product of normalized vectors = cosine similarity
    sim_tech = sum(a * b for a, b in zip(v1, v2, strict=False))
    sim_unrelated = sum(a * b for a, b in zip(v1, v3, strict=False))

    assert sim_tech > 0.40, f"Expected high similarity for related tech topics, got {sim_tech}"
    assert sim_tech > sim_unrelated, f"Expected tech similarity ({sim_tech}) > unrelated ({sim_unrelated})"


@pytest.mark.asyncio
async def test_memory_write_and_deduplication():
    """Test memory record creation, vector embedding, and exact duplicate prevention."""
    req1 = MemoryCreateRequest(
        memory_type=MemoryType.SEMANTIC,
        title="Candidate Skill: Python",
        content="Candidate has 8 years of Python experience building backend systems.",
        summary="Expert in Python backend",
        owner_scope=MemoryScope.APPLICANT_PROFILE,
        scope_id="app_123",
        verification_status=VerificationStatus.VERIFIED,
    )
    rec1 = await memory_service.write_memory(req1)
    assert rec1.id.startswith("mem_")
    assert rec1.embedding_status == "completed"

    # Attempt to write exact duplicate in the same scope
    rec2 = await memory_service.write_memory(req1)
    assert rec2.id == rec1.id, "Expected deduplication to return existing record ID"


@pytest.mark.asyncio
async def test_hybrid_and_keyword_retrieval():
    """Test hybrid, semantic, and keyword search over indexed memories."""
    # Write two distinct memories
    await memory_service.write_memory(
        MemoryCreateRequest(
            memory_type=MemoryType.SEMANTIC,
            title="TypeScript Fullstack",
            content="Built React 19 dashboards with Vite and TailwindCSS for financial analytics.",
            summary="React and TypeScript",
            owner_scope=MemoryScope.APPLICANT_PROFILE,
            scope_id="app_test_search",
            verification_status=VerificationStatus.VERIFIED,
        )
    )
    await memory_service.write_memory(
        MemoryCreateRequest(
            memory_type=MemoryType.SEMANTIC,
            title="Database Optimization",
            content="PostgreSQL and SQLite schema tuning, indexing, and query plan optimization.",
            summary="Database performance",
            owner_scope=MemoryScope.APPLICANT_PROFILE,
            scope_id="app_test_search",
            verification_status=VerificationStatus.VERIFIED,
        )
    )

    # 1. Hybrid Search
    res_hybrid = await memory_service.search_memory(
        MemorySearchRequest(
            query="React dashboard frontend",
            search_mode=SearchMode.HYBRID,
            scope_id="app_test_search",
        )
    )
    assert len(res_hybrid.results) >= 1
    assert "TypeScript" in res_hybrid.results[0].title or "React" in res_hybrid.results[0].content_snippet

    # 2. Keyword Search
    res_keyword = await memory_service.search_memory(
        MemorySearchRequest(
            query="SQLite indexing",
            search_mode=SearchMode.KEYWORD,
            scope_id="app_test_search",
        )
    )
    assert len(res_keyword.results) >= 1
    assert "Database" in res_keyword.results[0].title


@pytest.mark.asyncio
async def test_context_builder_budgeting():
    """Test ContextBuilder assembling structured sections and respecting token budgets."""
    await memory_service.write_memory(
        MemoryCreateRequest(
            memory_type=MemoryType.SEMANTIC,
            title="Verified Education",
            content="M.S. in Computer Science from Stanford University.",
            owner_scope=MemoryScope.APPLICANT_PROFILE,
            scope_id="app_budget_test",
            verification_status=VerificationStatus.VERIFIED,
        )
    )
    await memory_service.write_memory(
        MemoryCreateRequest(
            memory_type=MemoryType.PROCEDURAL,
            title="Resume Tailoring Procedure",
            content="1. Extract job keywords 2. Match skills 3. Quantify impact 4. Verify formatting.",
            owner_scope=MemoryScope.SHARED,
            scope_id="app_budget_test",
            verification_status=VerificationStatus.VERIFIED,
        )
    )

    ctx_res = await memory_service.build_context(
        ContextBuildRequest(
            task_description="Tailor resume for Computer Science position",
            agent_role="resume_agent",
            max_tokens=500,
        )
    )

    assert ctx_res.total_tokens > 0
    assert "[VERIFIED FACTS & PROFILE EVIDENCE]" in ctx_res.context_text
    assert len(ctx_res.records_used) >= 1


@pytest.mark.asyncio
async def test_conflict_detection_and_supersession():
    """Test contradiction recording and superseding older records."""
    rec1 = await memory_service.write_memory(
        MemoryCreateRequest(
            memory_type=MemoryType.SEMANTIC,
            title="Salary Preference",
            content="Target minimum base salary is $150,000 USD per year.",
            owner_scope=MemoryScope.USER,
            scope_id="user_conflict_test",
            verification_status=VerificationStatus.USER_CONFIRMED,
        )
    )

    # Write conflicting update
    rec2 = await memory_service.write_memory(
        MemoryCreateRequest(
            memory_type=MemoryType.SEMANTIC,
            title="Salary Preference",
            content="Updated target minimum base salary is $180,000 USD per year.",
            owner_scope=MemoryScope.USER,
            scope_id="user_conflict_test",
            verification_status=VerificationStatus.USER_CONFIRMED,
        )
    )

    # Check conflicts
    async with get_db_session() as session:
        repo = MemoryRepository(session)
        conflicts = await repo.list_conflicts()
        assert len(conflicts) >= 1

        # Supersede rec1 with rec2
        await conflict_resolver.supersede_memory(session, rec1.id, rec2.id)

    # Verify rec1 is superseded and excluded from standard search
    search_res = await memory_service.search_memory(
        MemorySearchRequest(
            query="Salary target",
            search_mode=SearchMode.HYBRID,
            scope_id="user_conflict_test",
            exclude_superseded=True,
        )
    )
    result_ids = [r.memory_id for r in search_res.results]
    assert rec1.id not in result_ids
    assert rec2.id in result_ids


@pytest.mark.asyncio
async def test_memory_expiration_and_deletion():
    """Test that expired memories are swept and deleted memories are evicted from active indexes."""
    # 1. Create a memory set to expire in the past
    unique_scope = f"task_temp_{uuid.uuid4().hex[:8]}"
    rec = await memory_service.write_memory(
        MemoryCreateRequest(
            memory_type=MemoryType.WORKING,
            title="Temporary Cache",
            content=f"Ephemeral context token {uuid.uuid4().hex}",
            owner_scope=MemoryScope.TASK,
            scope_id=unique_scope,
            retention_policy=RetentionPolicy.SESSION,
        )
    )
    # Manually backdate expiration
    async with get_db_session() as session:
        repo = MemoryRepository(session)
        await repo.update_memory(rec.id, {"expires_at": datetime.now(UTC) - timedelta(minutes=5)})
        swept = await expiration_manager.sweep_expired_memories(session)
        assert swept >= 1

    # Verify evicted from vector store
    assert vector_store.get(rec.id) is None

    # 2. Test explicit secure deletion
    rec_del = await memory_service.write_memory(
        MemoryCreateRequest(
            memory_type=MemoryType.SEMANTIC,
            title="Deletable Note",
            content="Sensitive secret data that must be scrubbed completely.",
            owner_scope=MemoryScope.USER,
            scope_id="user_del_test",
        )
    )
    assert vector_store.get(rec_del.id) is not None

    del_ok = await memory_service.delete_memory(rec_del.id, actor_id="user")
    assert del_ok is True
    assert vector_store.get(rec_del.id) is None

    # Search should return 0 results
    search_del = await memory_service.search_memory(
        MemorySearchRequest(
            query="Sensitive secret data",
            search_mode=SearchMode.HYBRID,
            scope_id="user_del_test",
        )
    )
    del_ids = [r.memory_id for r in search_del.results]
    assert rec_del.id not in del_ids
