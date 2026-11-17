"""Conflict detection, contradictions, and supersession management for agent memory."""

from datetime import UTC, datetime
import logging
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.contracts import VerificationStatus
from app.memory.storage.repository import MemoryRepository

logger = logging.getLogger("autonom.memory.lifecycle.conflicts")


class ConflictResolver:
    """Manages detection of contradictory memories and coordinates supersession."""

    async def detect_conflict(
        self,
        session: AsyncSession,
        new_title: str,
        new_content: str,
        scope_id: str,
        existing_memory_id: Optional[str] = None,
    ) -> Optional[str]:
        """Detects if an existing active memory in the same scope directly contradicts the new claim."""
        repo = MemoryRepository(session)
        # Look for memories with the same title or topic in the same scope
        memories = await repo.list_memories(scope_id=scope_id, limit=100)
        norm_title = new_title.strip().lower()

        for mem in memories:
            if existing_memory_id and mem.id == existing_memory_id:
                continue
            if mem.title.strip().lower() == norm_title and mem.content.strip() != new_content.strip():
                # Potential contradiction / preference change
                conflict = await repo.record_conflict(
                    memory_id_a=mem.id,
                    memory_id_b=existing_memory_id or "new_candidate",
                    conflict_type="contradiction",
                    description=f"Contradicting content detected for topic '{new_title}'",
                )
                logger.info(f"Recorded memory conflict '{conflict.id}' between '{mem.id}' and new candidate")
                return conflict.id
        return None

    async def supersede_memory(
        self,
        session: AsyncSession,
        old_memory_id: str,
        new_memory_id: str,
    ) -> bool:
        """Transitions older memory to superseded status and links it to the newer authoritative memory."""
        repo = MemoryRepository(session)
        old_record = await repo.get_memory_by_id(old_memory_id)
        if not old_record:
            return False

        await repo.update_memory(
            old_memory_id,
            {
                "verification_status": VerificationStatus.SUPERSEDED.value,
                "superseded_by": new_memory_id,
            },
        )
        logger.info(f"Memory '{old_memory_id}' successfully superseded by '{new_memory_id}'")
        return True


# Global singleton conflict resolver
conflict_resolver = ConflictResolver()
