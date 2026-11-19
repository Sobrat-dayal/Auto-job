"""Field Conflict Detection & Resolution Engine (Stage 27)."""

from datetime import UTC, datetime
from typing import Any, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CanonicalJobConflictModel
from app.recruitment.aggregation.contracts import ConflictResolutionStatus, ConflictType


class FieldConflictManager:
    """Detects and tracks field discrepancies across multiple source observations."""

    async def detect_conflicts(
        self,
        session: AsyncSession,
        canonical_job_id: str,
        field_values_by_source: dict[str, dict[str, Any]],
    ) -> list[CanonicalJobConflictModel]:
        """Examine field values from different sources and record conflicts if values clash."""
        conflicts: list[CanonicalJobConflictModel] = []

        # Check salary conflicts
        salaries = {src: data.get("salary") for src, data in field_values_by_source.items() if data.get("salary")}
        unique_salaries = set(salaries.values())
        if len(unique_salaries) > 1:
            conf = await self.record_conflict(
                session=session,
                canonical_job_id=canonical_job_id,
                field_name="compensation_summary",
                conflict_type=ConflictType.SALARY_MISMATCH,
                source_values=salaries,
            )
            conflicts.append(conf)

        # Check work arrangement conflicts (e.g. Remote vs Hybrid/Onsite)
        arrangements = {src: data.get("work_arrangement") for src, data in field_values_by_source.items() if data.get("work_arrangement")}
        unique_arrangements = set(arrangements.values())
        if len(unique_arrangements) > 1:
            conf = await self.record_conflict(
                session=session,
                canonical_job_id=canonical_job_id,
                field_name="work_arrangement",
                conflict_type=ConflictType.REMOTE_MISMATCH,
                source_values=arrangements,
            )
            conflicts.append(conf)

        return conflicts

    async def record_conflict(
        self,
        session: AsyncSession,
        canonical_job_id: str,
        field_name: str,
        conflict_type: ConflictType,
        source_values: dict[str, Any],
    ) -> CanonicalJobConflictModel:
        # Check if identical conflict already logged
        stmt = select(CanonicalJobConflictModel).where(
            CanonicalJobConflictModel.canonical_job_id == canonical_job_id,
            CanonicalJobConflictModel.field_name == field_name,
            CanonicalJobConflictModel.status == "unresolved",
        )
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()
        if existing:
            existing.source_values_json = source_values
            return existing

        conf = CanonicalJobConflictModel(
            canonical_job_id=canonical_job_id,
            field_name=field_name,
            conflict_type=conflict_type.value,
            status=ConflictResolutionStatus.UNRESOLVED.value,
            source_values_json=source_values,
            created_at=datetime.now(UTC),
        )
        session.add(conf)
        await session.flush()
        return conf

    async def resolve_conflict(
        self,
        session: AsyncSession,
        conflict_id: str,
        chosen_value: Any,
        resolution_note: str = "Resolved by user",
        resolved_by: str = "user_manual",
    ) -> Optional[CanonicalJobConflictModel]:
        stmt = select(CanonicalJobConflictModel).where(CanonicalJobConflictModel.id == conflict_id)
        res = await session.execute(stmt)
        conf = res.scalar_one_or_none()
        if not conf:
            return None

        conf.status = ConflictResolutionStatus.RESOLVED_BY_USER.value
        conf.resolution_note = resolution_note
        conf.resolved_by = resolved_by
        conf.resolved_at = datetime.now(UTC)
        await session.flush()
        return conf


field_conflict_manager = FieldConflictManager()
