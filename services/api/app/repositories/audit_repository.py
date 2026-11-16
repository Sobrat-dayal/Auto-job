"""Repository for immutable security and action audit logs."""

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AuditEventModel
from app.repositories.base import BaseRepository


class AuditRepository(BaseRepository[AuditEventModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def log_audit(
        self,
        action_type: str,
        resource_type: str,
        actor_id: str = "user",
        resource_id: str | None = None,
        outcome: str = "success",
        metadata: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> AuditEventModel:
        event = AuditEventModel(
            actor_id=actor_id,
            action_type=action_type,
            resource_type=resource_type,
            resource_id=resource_id,
            outcome=outcome,
            safe_metadata_json=metadata or {},
            correlation_id=correlation_id,
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def list_audits(self, limit: int = 50, offset: int = 0) -> list[AuditEventModel]:
        query = select(AuditEventModel).order_by(AuditEventModel.timestamp.desc()).limit(limit).offset(offset)
        result = await self.session.execute(query)
        return list(result.scalars().all())
