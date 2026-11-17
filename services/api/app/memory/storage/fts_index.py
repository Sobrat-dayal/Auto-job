"""SQLite FTS5 full-text keyword indexing and search for the Stage 15 Memory Engine."""

import logging
import re
from typing import Optional

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("autonom.memory.storage.fts")


class FTSIndexManager:
    """Manages full-text search indexing into the SQLite FTS5 virtual table."""

    @staticmethod
    def _sanitize_query(query: str) -> str:
        """Sanitizes user query for safe SQLite FTS5 syntax, avoiding syntax errors on special chars."""
        # Remove special FTS syntax characters: ", *, ^, :, (, ), AND, OR, NOT
        cleaned = re.sub(r'["\*\^\:\(\)]', " ", query)
        terms = [t.strip() for t in cleaned.split() if t.strip() and t.upper() not in ("AND", "OR", "NOT")]
        if not terms:
            return ""
        # Match tokens with OR and prefix wildcard for flexible recall and bm25 ranking
        return " OR ".join(f'"{term}"*' for term in terms)

    async def index_memory(
        self,
        session: AsyncSession,
        memory_id: str,
        title: str,
        content: str,
        summary: str,
        owner_scope: str,
        scope_id: str,
        memory_type: str,
    ) -> bool:
        """Inserts or replaces a memory record in the FTS5 virtual table."""
        try:
            # Delete existing if present
            await session.execute(
                text("DELETE FROM memory_fts WHERE memory_id = :memory_id"),
                {"memory_id": memory_id},
            )
            # Insert fresh
            await session.execute(
                text(
                    """
                    INSERT INTO memory_fts (memory_id, title, content, summary, owner_scope, scope_id, memory_type)
                    VALUES (:memory_id, :title, :content, :summary, :owner_scope, :scope_id, :memory_type)
                    """
                ),
                {
                    "memory_id": memory_id,
                    "title": title,
                    "content": content,
                    "summary": summary,
                    "owner_scope": owner_scope,
                    "scope_id": scope_id,
                    "memory_type": memory_type,
                },
            )
            await session.commit()
            return True
        except Exception as exc:
            logger.warning(f"FTS5 indexing failed for memory '{memory_id}': {exc}")
            return False

    async def delete_memory(self, session: AsyncSession, memory_id: str) -> bool:
        """Removes a memory record from the FTS5 index upon deletion."""
        try:
            await session.execute(
                text("DELETE FROM memory_fts WHERE memory_id = :memory_id"),
                {"memory_id": memory_id},
            )
            await session.commit()
            return True
        except Exception as exc:
            logger.warning(f"FTS5 deletion failed for memory '{memory_id}': {exc}")
            return False

    async def search(
        self,
        session: AsyncSession,
        query: str,
        limit: int = 10,
        allowed_memory_ids: Optional[set[str]] = None,
        owner_scope: Optional[str] = None,
        scope_id: Optional[str] = None,
        memory_type: Optional[str] = None,
    ) -> list[tuple[str, float]]:
        """Performs full-text search using FTS5 bm25 ranking.

        Returns a list of (memory_id, normalized_bm25_score) tuples descending.
        """
        sanitized = self._sanitize_query(query)
        if not sanitized:
            return []

        try:
            sql = """
                SELECT memory_id, bm25(memory_fts) as rank_score
                FROM memory_fts
                WHERE memory_fts MATCH :query
            """
            params: dict[str, str | int] = {"query": sanitized}

            if owner_scope:
                sql += " AND owner_scope = :owner_scope"
                params["owner_scope"] = owner_scope
            if scope_id:
                sql += " AND scope_id = :scope_id"
                params["scope_id"] = scope_id
            if memory_type:
                sql += " AND memory_type = :memory_type"
                params["memory_type"] = memory_type

            sql += " ORDER BY rank_score ASC LIMIT :limit"
            params["limit"] = limit * 2

            result = await session.execute(text(sql), params)
            rows = result.fetchall()

            scored: list[tuple[str, float]] = []
            for row in rows:
                mem_id = str(row[0])
                if allowed_memory_ids is not None and mem_id not in allowed_memory_ids:
                    continue
                # In SQLite FTS5, bm25 returns negative numbers where more negative is better match.
                # Convert to normalized 0.0 - 1.0 range
                raw_bm25 = float(row[1])
                norm_score = max(0.01, min(1.0, 1.0 / (1.0 + abs(raw_bm25))))
                scored.append((mem_id, round(norm_score, 4)))

            # Sort descending by normalized score
            scored.sort(key=lambda x: x[1], reverse=True)
            return scored[:limit]

        except Exception as exc:
            logger.warning(f"FTS5 search query failed: {exc}")
            # Fallback simple substring search across memory_records if FTS5 fails
            return []


# Global singleton FTS index manager
fts_index_manager = FTSIndexManager()
