"""Merge Preview and Impact Analysis Engine (Stage 27)."""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CanonicalJobSourceLinkModel
from app.recruitment.aggregation.canonical.registry import canonical_job_registry
from app.recruitment.aggregation.contracts import MergePreviewResponse
from app.recruitment.aggregation.errors import CanonicalJobNotFoundError, CircularMergeError


class MergePreviewEngine:
    """Calculates the consequences and safety of a proposed canonical job merge."""

    async def preview_merge(
        self,
        session: AsyncSession,
        surviving_job_id: str,
        superseded_job_id: str,
    ) -> MergePreviewResponse:
        if surviving_job_id == superseded_job_id:
            raise CircularMergeError("Cannot merge a canonical job into itself")

        surviving = await canonical_job_registry.get_by_id(session, surviving_job_id)
        if not surviving:
            raise CanonicalJobNotFoundError(f"Surviving job {surviving_job_id} not found")

        superseded = await canonical_job_registry.get_by_id(session, superseded_job_id)
        if not superseded:
            raise CanonicalJobNotFoundError(f"Superseded job {superseded_job_id} not found")

        stmt_links = select(CanonicalJobSourceLinkModel).where(
            CanonicalJobSourceLinkModel.canonical_job_id == superseded_job_id,
            CanonicalJobSourceLinkModel.association_status == "active",
        )
        res_links = await session.execute(stmt_links)
        superseded_links = list(res_links.scalars().all())

        transfer_links = [l.id for l in superseded_links]
        resulting_count = surviving.source_count + len(transfer_links)

        warnings: list[str] = []
        conflicts: list[dict[str, str]] = []

        if surviving.employer_id != superseded.employer_id:
            warnings.append(
                f"Merged jobs currently belong to different employers ({surviving.employer_id} vs {superseded.employer_id})."
            )

        if surviving.compensation_summary and superseded.compensation_summary:
            if surviving.compensation_summary != superseded.compensation_summary:
                conflicts.append({
                    "field": "compensation_summary",
                    "surviving": surviving.compensation_summary,
                    "superseded": superseded.compensation_summary,
                })

        return MergePreviewResponse(
            surviving_job_id=surviving.id,
            superseded_job_id=superseded.id,
            proposed_title=surviving.display_title,
            proposed_employer_id=surviving.employer_id,
            resulting_source_count=resulting_count,
            source_links_to_transfer=transfer_links,
            detected_conflicts=conflicts,
            affected_downstream_references=[],
            is_safe_to_merge=len(conflicts) == 0,
            warnings=warnings,
        )


merge_preview_engine = MergePreviewEngine()
