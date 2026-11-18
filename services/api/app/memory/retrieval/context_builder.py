"""Context Builder selecting and formatting relevant, authorized memory within token budgets."""

import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.contracts import (
    ContextBuildRequest,
    ContextBuildResponse,
    MemoryScope,
    MemoryType,
    SearchMode,
)
from app.memory.embeddings.registry import embedding_registry
from app.memory.retrieval.hybrid import hybrid_retrieval_engine
from app.memory.storage.repository import MemoryRepository

logger = logging.getLogger("autonom.memory.retrieval.context_builder")


class ContextBuilder:
    """Selects, deduplicates, and formats task-relevant memories into structured prompt context."""

    def __init__(self) -> None:
        self.retrieval_engine = hybrid_retrieval_engine

    @staticmethod
    def _estimate_tokens(text: str) -> int:
        """Rough token estimate: ~4 characters per token."""
        return max(1, len(text) // 4)

    async def build_context(
        self,
        session: AsyncSession,
        request: ContextBuildRequest,
        allowed_memory_ids: Optional[set[str]] = None,
    ) -> ContextBuildResponse:
        """Retrieves and structures authorized memory context for an agent execution."""
        repo = MemoryRepository(session)
        provider = embedding_registry.get_active_provider()

        target_scope_id = request.scope_ids[0] if (request.scope_ids and len(request.scope_ids) == 1) else None

        # 1. Search for relevant memories matching task description
        search_results = await self.retrieval_engine.search(
            session=session,
            query=request.task_description,
            embedding_provider=provider,
            search_mode=SearchMode.HYBRID,
            memory_types=request.memory_types,
            scope_id=target_scope_id,
            allowed_memory_ids=allowed_memory_ids,
            exclude_superseded=True,
            min_score=0.0 if request.scope_ids else 0.15,
            limit=25,
        )

        # 2. Categorize candidates into evidence buckets
        facts: list[str] = []
        procedures: list[str] = []
        episodes: list[str] = []
        used_ids: list[str] = []
        seen_titles: set[str] = set()

        total_tokens = 0
        truncated = False

        for item in search_results:
            # Simple deduplication by title/topic
            norm_title = item.title.strip().lower()
            if norm_title in seen_titles:
                continue
            seen_titles.add(norm_title)

            record = await repo.get_memory_by_id(item.memory_id)
            if not record:
                continue

            if request.scope_ids and record.scope_id and record.scope_id not in request.scope_ids:
                continue

            entry_text = f"- {record.title}: {record.content} [Verification: {record.verification_status}, Source: {record.source_type}]"
            entry_tokens = self._estimate_tokens(entry_text)

            if total_tokens + entry_tokens > request.max_tokens:
                truncated = True
                break

            if record.memory_type == MemoryType.SEMANTIC.value:
                facts.append(entry_text)
            elif record.memory_type == MemoryType.PROCEDURAL.value:
                procedures.append(entry_text)
            elif record.memory_type in (MemoryType.EPISODIC.value, MemoryType.WORKING.value):
                episodes.append(entry_text)

            used_ids.append(record.id)
            total_tokens += entry_tokens

        # 3. Assemble formatted context blocks
        sections: list[str] = []

        if facts:
            sections.append("### [VERIFIED FACTS & PROFILE EVIDENCE]\n" + "\n".join(facts))
        if procedures:
            sections.append("### [REUSABLE PROCEDURES & VALIDATED METHODS]\n" + "\n".join(procedures))
        if episodes:
            sections.append("### [PRIOR WORKFLOW EXPERIENCES & LESSONS]\n" + "\n".join(episodes))

        final_context = "\n\n".join(sections) if sections else ""

        return ContextBuildResponse(
            context_text=final_context,
            records_used=used_ids,
            total_tokens=self._estimate_tokens(final_context),
            facts_count=len(facts),
            procedures_count=len(procedures),
            episodes_count=len(episodes),
            truncated=truncated,
        )


# Global singleton context builder
context_builder = ContextBuilder()
