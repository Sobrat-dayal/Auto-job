"""Repository for persistent task event history."""

from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import TaskEventModel
from app.repositories.base import BaseRepository


class TaskEventRepository(BaseRepository[TaskEventModel]):
    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def record_event(
        self,
        task_id: str,
        event_type: str,
        state_transition: str | None = None,
        metadata: dict[str, Any] | None = None,
        correlation_id: str | None = None,
    ) -> TaskEventModel:
        # Determine sequence number
        seq_query = select(func.coalesce(func.max(TaskEventModel.sequence_num), 0)).where(
            TaskEventModel.task_id == task_id
        )
        current_seq = (await self.session.execute(seq_query)).scalar() or 0

        event = TaskEventModel(
            task_id=task_id,
            event_type=event_type,
            state_transition=state_transition,
            metadata_json=metadata or {},
            correlation_id=correlation_id,
            sequence_num=current_seq + 1,
        )
        self.session.add(event)
        await self.session.flush()
        return event

    async def list_events_for_task(self, task_id: str) -> list[TaskEventModel]:
        query = (
            select(TaskEventModel).where(TaskEventModel.task_id == task_id).order_by(TaskEventModel.sequence_num.asc())
        )
        result = await self.session.execute(query)
        return list(result.scalars().all())
