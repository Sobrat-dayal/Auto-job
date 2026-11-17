"""Hybrid retrieval engine combining full-text keyword matching and dense vector similarity."""

from datetime import UTC, datetime
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.contracts import (
    MemoryScope,
    MemorySearchResultItem,
    MemoryType,
    SearchMode,
    SensitivityCategory,
    VerificationStatus,
)
from app.memory.embeddings.provider import BaseEmbeddingProvider
from app.memory.storage.fts_index import FTSIndexManager, fts_index_manager
from app.memory.storage.repository import MemoryRepository
from app.memory.storage.vector_store import VectorStore, vector_store

logger = logging.getLogger("autonom.memory.retrieval.hybrid")


class HybridRetrievalEngine:
    """Orchestrates hybrid, semantic, and keyword retrieval with epistemic weighting."""

    def __init__(
        self,
        vector_index: VectorStore = vector_store,
        fts_index: FTSIndexManager = fts_index_manager,
    ) -> None:
        self.vector_index = vector_index
        self.fts_index = fts_index

    async def search(
        self,
        session: AsyncSession,
        query: str,
        embedding_provider: BaseEmbeddingProvider,
        search_mode: SearchMode = SearchMode.HYBRID,
        memory_types: Optional[list[MemoryType]] = None,
        owner_scope: Optional[MemoryScope] = None,
        scope_id: Optional[str] = None,
        allowed_memory_ids: Optional[set[str]] = None,
        exclude_superseded: bool = True,
        min_score: float = 0.0,
        limit: int = 10,
    ) -> list[MemorySearchResultItem]:
        """Executes search across vector store and/or FTS5 index and applies rank fusion."""
        repo = MemoryRepository(session)

        # 1. Scope filter mapping
        scope_filter_dict: dict[str, str] = {}
        if owner_scope:
            scope_filter_dict["owner_scope"] = owner_scope.value
        if scope_id:
            scope_filter_dict["scope_id"] = scope_id

        vector_results: list[tuple[str, float]] = []
        keyword_results: list[tuple[str, float]] = []

        # 2. Vector search branch
        if search_mode in (SearchMode.HYBRID, SearchMode.SEMANTIC):
            try:
                q_vec = await embedding_provider.embed_text(query)
                vector_results = self.vector_index.search(
                    query_embedding=q_vec,
                    limit=limit * 3,
                    allowed_memory_ids=allowed_memory_ids,
                    scope_filters=scope_filter_dict if scope_filter_dict else None,
                    min_similarity=0.01,
                )
            except Exception as exc:
                logger.warning(f"Vector search execution error: {exc}")
                vector_results = []

        # 3. Keyword search branch
        if search_mode in (SearchMode.HYBRID, SearchMode.KEYWORD):
            try:
                keyword_results = await self.fts_index.search(
                    session=session,
                    query=query,
                    limit=limit * 3,
                    allowed_memory_ids=allowed_memory_ids,
                    owner_scope=owner_scope.value if owner_scope else None,
                    scope_id=scope_id,
                )
            except Exception as exc:
                logger.warning(f"Keyword search execution error: {exc}")
                keyword_results = []

        # 4. Score Fusion (Reciprocal Rank Fusion)
        # RRF score = sum(weight / (k + rank))
        k = 60.0
        weight_vec = 0.6 if search_mode == SearchMode.HYBRID else (1.0 if search_mode == SearchMode.SEMANTIC else 0.0)
        weight_kw = 0.4 if search_mode == SearchMode.HYBRID else (1.0 if search_mode == SearchMode.KEYWORD else 0.0)

        fused_scores: dict[str, float] = {}
        vec_score_map: dict[str, float] = dict(vector_results)
        kw_score_map: dict[str, float] = dict(keyword_results)

        for rank, (mem_id, _score) in enumerate(vector_results, 1):
            fused_scores[mem_id] = fused_scores.get(mem_id, 0.0) + (weight_vec / (k + rank))

        for rank, (mem_id, _score) in enumerate(keyword_results, 1):
            fused_scores[mem_id] = fused_scores.get(mem_id, 0.0) + (weight_kw / (k + rank))

        if not fused_scores:
            return []

        # 5. Fetch full records to verify filters, types, supersession, and epistemic weighting
        all_candidate_ids = list(fused_scores.keys())
        results: list[MemorySearchResultItem] = []

        for mem_id in all_candidate_ids:
            record = await repo.get_memory_by_id(mem_id)
            if not record or record.is_deleted:
                continue

            # Check supersession
            if exclude_superseded and (
                record.superseded_by is not None or record.verification_status == "superseded"
            ):
                continue

            # Check memory types filter
            if memory_types and record.memory_type not in [t.value for t in memory_types]:
                continue

            # Base normalized score
            raw_fused = fused_scores[mem_id]
            # Rescale RRF score to 0.0 - 1.0 range
            max_possible = (weight_vec / (k + 1)) + (weight_kw / (k + 1))
            normalized_score = min(1.0, raw_fused / max_possible if max_possible > 0 else 0.0)

            # Epistemic & Verification Status adjustment
            status_boost = 0.0
            if record.verification_status in ("verified", "user_confirmed"):
                status_boost = 0.10
            elif record.verification_status == "evidence_supported":
                status_boost = 0.05
            elif record.verification_status == "unverified":
                status_boost = -0.05
            elif record.verification_status in ("conflicted", "rejected"):
                status_boost = -0.20

            final_score = max(0.0, min(1.0, normalized_score + status_boost))

            if final_score < min_score:
                continue

            # Build snippet
            snippet = record.content[:300] + ("..." if len(record.content) > 300 else "")

            results.append(
                MemorySearchResultItem(
                    memory_id=record.id,
                    title=record.title,
                    content_snippet=snippet,
                    memory_type=MemoryType(record.memory_type),
                    owner_scope=MemoryScope(record.owner_scope),
                    scope_id=record.scope_id,
                    verification_status=VerificationStatus(record.verification_status),
                    sensitivity_category=SensitivityCategory(record.sensitivity_category),
                    similarity_score=vec_score_map.get(record.id, 0.0),
                    keyword_score=kw_score_map.get(record.id, 0.0),
                    combined_score=round(final_score, 4),
                    provenance=record.provenance_json or {},
                    created_at=record.created_at,
                )
            )

        # Sort descending by combined score
        results.sort(key=lambda x: x.combined_score, reverse=True)
        return results[:limit]


# Global singleton hybrid retrieval engine
hybrid_retrieval_engine = HybridRetrievalEngine()
