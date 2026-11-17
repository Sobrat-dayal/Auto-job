"""Memory expiration and retention sweep lifecycle service."""

from datetime import UTC, datetime
import logging

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import MemoryRecord
from app.memory.contracts import VerificationStatus
from app.memory.storage.fts_index import fts_index_manager
from app.memory.storage.vector_store import vector_store

logger = logging.getLogger("autonom.memory.lifecycle.expiration")


class ExpirationManager:
    """Identifies and purges or transitions expired memories."""

    async def sweep_expired_memories(self, session: AsyncSession) -> int:
        """Finds records with passed expiration timestamps, marks them expired, and evicts from active indices."""
        now = datetime.now(UTC).replace(tzinfo=None)
        stmt = (
            select(MemoryRecord)
            .where(
                MemoryRecord.expires_at.is_not(None),
                MemoryRecord.expires_at <= now,
                MemoryRecord.verification_status != VerificationStatus.EXPIRED.value,
                MemoryRecord.is_deleted.is_(False),
            )
        )
        result = await session.execute(stmt)
        expired_records = list(result.scalars().all())

        count = 0
        for rec in expired_records:
            rec.verification_status = VerificationStatus.EXPIRED.value
            rec.updated_at = now
            # Evict from active vector store & FTS5
            vector_store.delete(rec.id)
            await fts_index_manager.delete_memory(session, rec.id)
            count += 1

        if count > 0:
            await session.commit()
            logger.info(f"Swept {count} expired memory records from active indexes.")

        return count


# Global singleton expiration manager
expiration_manager = ExpirationManager()
