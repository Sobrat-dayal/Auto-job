"""Deduplication logic using content hashing and cosine similarity thresholds."""

import hashlib
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.storage.repository import MemoryRepository
from app.memory.storage.vector_store import vector_store

logger = logging.getLogger("autonom.memory.lifecycle.deduplication")


class DeduplicationService:
    """Detects exact and semantic near-duplicates to prevent memory bloat."""

    @staticmethod
    def compute_checksum(content: str) -> str:
        """Computes deterministic SHA-256 hash of normalized text."""
        normalized = " ".join(content.strip().lower().split())
        return hashlib.sha256(normalized.encode("utf-8")).hexdigest()

    async def find_exact_duplicate(
        self,
        session: AsyncSession,
        content: str,
        scope_id: str,
    ) -> Optional[str]:
        """Checks if a memory with the exact same content exists within the scope."""
        repo = MemoryRepository(session)
        checksum = self.compute_checksum(content)
        existing = await repo.find_by_checksum(checksum, scope_id)
        return existing.id if existing else None

    def find_near_duplicates(
        self,
        query_embedding: list[float],
        scope_id: str,
        threshold: float = 0.95,
    ) -> list[tuple[str, float]]:
        """Identifies near-duplicate memories in the vector index with similarity exceeding threshold."""
        matches = vector_store.search(
            query_embedding=query_embedding,
            limit=5,
            scope_filters={"scope_id": scope_id},
            min_similarity=threshold,
        )
        return matches


# Global singleton deduplication service
deduplication_service = DeduplicationService()
