"""Distributed-safe worker leasing system backed by SQLite."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import logging
from typing import Optional
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.models import RecruitmentWorkerLeaseModel
from app.recruitment.monitoring.errors import LeaseConflictError

logger = logging.getLogger("autonom.recruitment.monitoring.execution.leases")


def to_utc(dt: Optional[datetime]) -> Optional[datetime]:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=UTC)
    return dt.astimezone(UTC)


class LeaseManager:
    """Manages atomic, expiring task leases for concurrent worker coordination."""

    def __init__(self, lease_duration_seconds: int = 120) -> None:
        self.lease_duration_seconds = lease_duration_seconds

    async def acquire_lease(
        self,
        lease_key: str,
        worker_id: str,
        session: AsyncSession,
    ) -> bool:
        """Attempts to atomically acquire a lease key. Returns True if acquired, False if currently held."""
        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=self.lease_duration_seconds)

        stmt = select(RecruitmentWorkerLeaseModel).where(RecruitmentWorkerLeaseModel.lease_key == lease_key)
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            # Check if expired
            exp = to_utc(existing.expires_at)
            if exp and exp < now:
                # Reclaim expired lease
                existing.owner_worker_id = worker_id
                existing.acquired_at = now
                existing.expires_at = expires_at
                existing.heartbeat_at = now
                existing.attempt_number += 1
                await session.flush()
                logger.info(f"Reclaimed expired lease '{lease_key}' for worker '{worker_id}'")
                return True
            elif existing.owner_worker_id == worker_id:
                # Renew own lease
                existing.expires_at = expires_at
                existing.heartbeat_at = now
                await session.flush()
                return True
            else:
                # Active lease held by another worker
                return False

        # Create new lease
        lease = RecruitmentWorkerLeaseModel(
            lease_key=lease_key,
            owner_worker_id=worker_id,
            acquired_at=now,
            expires_at=expires_at,
            heartbeat_at=now,
            attempt_number=1,
        )
        session.add(lease)
        try:
            await session.flush()
            logger.info(f"Acquired new lease '{lease_key}' for worker '{worker_id}'")
            return True
        except Exception:
            # Race condition on unique constraint
            return False

    async def heartbeat(
        self,
        lease_key: str,
        worker_id: str,
        session: AsyncSession,
    ) -> bool:
        """Extends an actively held lease."""
        now = datetime.now(UTC)
        expires_at = now + timedelta(seconds=self.lease_duration_seconds)

        stmt = select(RecruitmentWorkerLeaseModel).where(
            RecruitmentWorkerLeaseModel.lease_key == lease_key,
            RecruitmentWorkerLeaseModel.owner_worker_id == worker_id,
        )
        res = await session.execute(stmt)
        lease = res.scalar_one_or_none()
        if not lease:
            return False

        lease.heartbeat_at = now
        lease.expires_at = expires_at
        await session.flush()
        return True

    async def release_lease(
        self,
        lease_key: str,
        worker_id: str,
        session: AsyncSession,
    ) -> bool:
        """Voluntarily releases a task lease upon completion."""
        stmt = delete(RecruitmentWorkerLeaseModel).where(
            RecruitmentWorkerLeaseModel.lease_key == lease_key,
            RecruitmentWorkerLeaseModel.owner_worker_id == worker_id,
        )
        res = await session.execute(stmt)
        await session.flush()
        return res.rowcount > 0

    async def clear_expired_leases(self, session: AsyncSession) -> int:
        """Cleanup worker to purge expired leases."""
        now = datetime.now(UTC)
        stmt = delete(RecruitmentWorkerLeaseModel).where(RecruitmentWorkerLeaseModel.expires_at < now)
        res = await session.execute(stmt)
        await session.flush()
        return res.rowcount


lease_manager = LeaseManager()
