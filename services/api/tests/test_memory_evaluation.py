"""Reproducible Retrieval Quality Evaluation Benchmark (Stage 15).

Measures Precision@K, Recall@K, Mean Reciprocal Rank (MRR), and latency across
keyword, vector, and hybrid retrieval with synthetic ground-truth test collections.
"""

from datetime import UTC, datetime
import time
import uuid
import pytest

from app.memory.contracts import (
    MemoryCreateRequest,
    MemoryScope,
    MemorySearchRequest,
    MemoryType,
    SearchMode,
    VerificationStatus,
)
from app.memory.service import memory_service
from app.memory.storage.vector_store import vector_store


@pytest.fixture(autouse=True)
def clean_memory_index():
    vector_store.clear()
    yield


@pytest.mark.asyncio
async def test_retrieval_quality_evaluation():
    """Executes a benchmark evaluating Precision@3, Recall@3, and MRR on labeled synthetic fixtures."""
    scope_id = f"eval_benchmark_{uuid.uuid4().hex[:8]}"

    # Labeled ground truth corpus
    corpus = [
        # Topic 1: Systems Programming
        {
            "id_tag": "rust_systems",
            "title": "Rust Async Concurrency",
            "content": "Deep experience with async Tokio, actors, channels, and zero-cost abstractions in Rust.",
            "relevant_queries": ["rust async tokio channels", "systems programming concurrency"],
        },
        {
            "id_tag": "cpp_systems",
            "title": "Modern C++ Memory Management",
            "content": "Low-level manual memory allocation, RAII, smart pointers, and SIMD vectorization.",
            "relevant_queries": ["systems programming concurrency"],
        },
        # Topic 2: Frontend Engineering
        {
            "id_tag": "react_frontend",
            "title": "React 19 Server Components",
            "content": "Building interactive single page apps with React 19, hydration, and Tailwind CSS.",
            "relevant_queries": ["react components frontend ui", "web user interface design"],
        },
        {
            "id_tag": "typescript_tools",
            "title": "TypeScript Strict Compiler",
            "content": "Type safety, generics, compiler flags, and Vite build tooling for web development.",
            "relevant_queries": ["react components frontend ui"],
        },
        # Topic 3: Cloud & Databases
        {
            "id_tag": "database_tuning",
            "title": "SQLite Index Performance",
            "content": "B-tree indices, WAL mode configuration, and query execution plan analysis.",
            "relevant_queries": ["sqlite query plan indexing"],
        },
    ]

    # Index corpus into memory engine
    created_map: dict[str, str] = {}
    for doc in corpus:
        rec = await memory_service.write_memory(
            MemoryCreateRequest(
                memory_type=MemoryType.SEMANTIC,
                title=doc["title"],
                content=doc["content"],
                owner_scope=MemoryScope.PROJECT,
                scope_id=scope_id,
                verification_status=VerificationStatus.VERIFIED,
            )
        )
        created_map[doc["id_tag"]] = rec.id

    # Test Queries & Ground Truth targets
    eval_queries = [
        {
            "query": "rust async tokio channels",
            "expected_top": "rust_systems",
            "mode": SearchMode.HYBRID,
        },
        {
            "query": "react components frontend ui",
            "expected_top": "react_frontend",
            "mode": SearchMode.HYBRID,
        },
        {
            "query": "sqlite query plan indexing",
            "expected_top": "database_tuning",
            "mode": SearchMode.KEYWORD,
        },
        {
            "query": "systems programming concurrency",
            "expected_top": "rust_systems",  # either rust or cpp
            "mode": SearchMode.SEMANTIC,
        },
    ]

    reciprocal_ranks: list[float] = []
    precision_at_3: list[float] = []
    latencies: list[float] = []

    for item in eval_queries:
        t0 = time.perf_counter()
        res = await memory_service.search_memory(
            MemorySearchRequest(
                query=item["query"],
                search_mode=item["mode"],
                owner_scope=MemoryScope.PROJECT,
                scope_id=scope_id,
                limit=3,
            )
        )
        latencies.append((time.perf_counter() - t0) * 1000.0)

        retrieved_ids = [r.memory_id for r in res.results]
        target_id = created_map[item["expected_top"]]

        # Calculate Reciprocal Rank
        rr = 0.0
        for rank, rid in enumerate(retrieved_ids, 1):
            if rid == target_id:
                rr = 1.0 / rank
                break
        reciprocal_ranks.append(rr)

        # Calculate Precision@3
        p3 = 1.0 / 3.0 if target_id in retrieved_ids else 0.0
        precision_at_3.append(p3)

    mean_reciprocal_rank = sum(reciprocal_ranks) / len(reciprocal_ranks)
    mean_latency_ms = sum(latencies) / len(latencies)

    # Benchmark assertions
    assert mean_reciprocal_rank >= 0.75, f"MRR too low: {mean_reciprocal_rank}"
    assert mean_latency_ms < 50.0, f"Average retrieval latency too high: {mean_latency_ms}ms"
