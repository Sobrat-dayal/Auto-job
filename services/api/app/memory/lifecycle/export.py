"""Structured memory export service honoring data classifications and privacy limits."""

import json
import logging
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.contracts import MemoryScope, SensitivityCategory
from app.memory.storage.repository import MemoryRepository

logger = logging.getLogger("autonom.memory.lifecycle.export")


class ExportService:
    """Exports authorized memories into JSON or JSON-Lines formats."""

    async def export_memories(
        self,
        session: AsyncSession,
        owner_scope: Optional[MemoryScope] = None,
        scope_id: Optional[str] = None,
        include_sensitive: bool = False,
    ) -> list[dict[str, Any]]:
        """Serializes permitted memory records into an exportable dictionary list."""
        repo = MemoryRepository(session)
        records = await repo.list_memories(
            owner_scope=owner_scope.value if owner_scope else None,
            scope_id=scope_id,
            limit=5000,
        )

        exported: list[dict[str, Any]] = []
        for r in records:
            if not include_sensitive and r.sensitivity_category in (
                SensitivityCategory.RESTRICTED.value,
                SensitivityCategory.SECRET.value,
            ):
                continue

            exported.append(
                {
                    "id": r.id,
                    "memory_type": r.memory_type,
                    "title": r.title,
                    "content": r.content,
                    "summary": r.summary,
                    "owner_scope": r.owner_scope,
                    "scope_id": r.scope_id,
                    "source_type": r.source_type,
                    "source_ref": r.source_ref,
                    "verification_status": r.verification_status,
                    "confidence_category": r.confidence_category,
                    "sensitivity_category": r.sensitivity_category,
                    "created_at": r.created_at.isoformat(),
                    "updated_at": r.updated_at.isoformat(),
                    "version": r.version,
                    "provenance": r.provenance_json or {},
                    "metadata": r.metadata_json or {},
                }
            )

        return exported


# Global singleton export service
export_service = ExportService()
