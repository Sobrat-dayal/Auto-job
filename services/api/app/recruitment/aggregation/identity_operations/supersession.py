"""Canonical ID Supersession & Alias Resolution Engine (Stage 27)."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CanonicalJobAliasModel


class SupersessionManager:
    """Resolves superseded canonical job IDs to surviving identities without breaking references."""

    async def resolve_active_id(self, session: AsyncSession, job_id: str, max_depth: int = 5) -> str:
        """Trace alias pointers to find the surviving canonical ID (handles chained merges safely)."""
        current_id = job_id
        depth = 0

        while depth < max_depth:
            stmt = select(CanonicalJobAliasModel).where(CanonicalJobAliasModel.alias_id == current_id)
            res = await session.execute(stmt)
            alias = res.scalar_one_or_none()
            if not alias:
                break
            current_id = alias.target_job_id
            depth += 1

        return current_id

    async def create_alias(self, session: AsyncSession, superseded_id: str, surviving_id: str) -> CanonicalJobAliasModel:
        alias = CanonicalJobAliasModel(
            alias_id=superseded_id,
            target_job_id=surviving_id,
        )
        session.add(alias)
        await session.flush()
        return alias


supersession_manager = SupersessionManager()
