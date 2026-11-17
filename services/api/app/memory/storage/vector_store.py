"""Vector storage and cosine similarity search engine for the Stage 15 Memory Engine."""

import logging
import math
from typing import Any, Optional

logger = logging.getLogger("autonom.memory.storage.vector_store")


class VectorItem:
    """Indexed vector representation with memory metadata references."""

    def __init__(
        self,
        memory_id: str,
        embedding: list[float],
        model_id: str,
        owner_scope: str,
        scope_id: str,
        is_deleted: bool = False,
    ) -> None:
        self.memory_id = memory_id
        self.embedding = embedding
        self.model_id = model_id
        self.owner_scope = owner_scope
        self.scope_id = scope_id
        self.is_deleted = is_deleted


class VectorStore:
    """Fast in-memory and SQLite-synchronized vector index with cosine similarity search.

    Engineered specifically for Windows 11 desktop environments without requiring
    unstable native C++ extensions or separate vector database daemons.
    """

    def __init__(self, expected_dimension: int = 384) -> None:
        self.expected_dimension = expected_dimension
        self._index: dict[str, VectorItem] = {}

    def upsert(
        self,
        memory_id: str,
        embedding: list[float],
        model_id: str,
        owner_scope: str,
        scope_id: str,
    ) -> bool:
        """Inserts or updates a vector in the index after validating dimensions."""
        if len(embedding) != self.expected_dimension:
            logger.error(
                f"Vector dimension mismatch for memory '{memory_id}': "
                f"expected {self.expected_dimension}, got {len(embedding)}"
            )
            return False

        # Ensure normalized
        norm = math.sqrt(sum(x * x for x in embedding))
        normalized = [x / norm for x in embedding] if norm > 1e-9 else embedding

        self._index[memory_id] = VectorItem(
            memory_id=memory_id,
            embedding=normalized,
            model_id=model_id,
            owner_scope=owner_scope,
            scope_id=scope_id,
            is_deleted=False,
        )
        return True

    def delete(self, memory_id: str) -> bool:
        """Removes a vector from the index."""
        if memory_id in self._index:
            del self._index[memory_id]
            return True
        return False

    def get(self, memory_id: str) -> Optional[VectorItem]:
        return self._index.get(memory_id)

    def size(self) -> int:
        return len(self._index)

    def clear(self) -> None:
        self._index.clear()

    def search(
        self,
        query_embedding: list[float],
        limit: int = 10,
        model_id: Optional[str] = None,
        allowed_memory_ids: Optional[set[str]] = None,
        scope_filters: Optional[dict[str, str]] = None,
        min_similarity: float = 0.0,
    ) -> list[tuple[str, float]]:
        """Performs cosine similarity search against indexed vectors.

        Returns a sorted list of (memory_id, similarity_score) tuples descending.
        """
        if len(query_embedding) != self.expected_dimension:
            logger.warning(
                f"Query vector dimension mismatch: expected {self.expected_dimension}, "
                f"got {len(query_embedding)}"
            )
            return []

        # Normalize query vector
        q_norm = math.sqrt(sum(x * x for x in query_embedding))
        q_vec = [x / q_norm for x in query_embedding] if q_norm > 1e-9 else query_embedding

        results: list[tuple[str, float]] = []

        for mem_id, item in self._index.items():
            if item.is_deleted:
                continue
            if model_id and item.model_id != model_id:
                continue
            if allowed_memory_ids is not None and mem_id not in allowed_memory_ids:
                continue
            if scope_filters:
                if "owner_scope" in scope_filters and item.owner_scope != scope_filters["owner_scope"]:
                    continue
                if "scope_id" in scope_filters and item.scope_id != scope_filters["scope_id"]:
                    continue

            # Normalized dot product = cosine similarity
            sim = sum(q * v for q, v in zip(q_vec, item.embedding, strict=False))
            # Clamp between 0.0 and 1.0
            clamped_sim = max(0.0, min(1.0, (sim + 1.0) / 2.0 if sim < 0 else sim))

            if clamped_sim >= min_similarity:
                results.append((mem_id, round(clamped_sim, 4)))

        # Sort descending by similarity
        results.sort(key=lambda x: x[1], reverse=True)
        return results[:limit]


# Global singleton vector store
vector_store = VectorStore(expected_dimension=384)
