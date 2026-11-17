"""Secure cascading deletion coordinator for agent memory records."""

from datetime import UTC, datetime
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.storage.fts_index import fts_index_manager
from app.memory.storage.repository import MemoryRepository
from app.memory.storage.vector_store import vector_store

logger = logging.getLogger("autonom.memory.lifecycle.deletion")


class DeletionCoordinator:
    """Coordinates secure memory deletion across SQLite, FTS5, vector store, and audit events."""

    async def delete_memory(
        self,
        session: AsyncSession,
        memory_id: str,
        actor_id: str = "user",
        reason: str = "User requested deletion",
    ) -> bool:
        """Performs cascading removal of a memory record and purges its search representations."""
        repo = MemoryRepository(session)
        record = await repo.get_memory_by_id(memory_id)
        if not record or record.is_deleted:
            return False

        # 1. Soft-delete primary record
        await repo.soft_delete_memory(memory_id)

        # 2. Evict from vector store
        vector_store.delete(memory_id)

        # 3. Purge from FTS5 index
        await fts_index_manager.delete_memory(session, memory_id)

        # 4. Record audit event
        await repo.log_access_event(
            action="delete",
            outcome="allowed",
            actor_id=actor_id,
            memory_id=memory_id,
            reason=reason,
        )

        logger.info(f"Memory record '{memory_id}' securely deleted and purged from all search indices.")
        return True


# Global singleton deletion coordinator
deletion_coordinator = DeletionCoordinator()
