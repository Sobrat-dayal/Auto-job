"""Split / Unmerge Preview Engine (Stage 27)."""

from sqlalchemy.ext.asyncio import AsyncSession

from app.recruitment.aggregation.canonical.registry import canonical_job_registry
from app.recruitment.aggregation.contracts import SplitPreviewResponse
from app.recruitment.aggregation.errors import CanonicalJobNotFoundError


class SplitPreviewEngine:
    """Previews the impact of detaching sources or splitting a merged canonical job."""

    async def preview_split(
        self,
        session: AsyncSession,
        canonical_job_id: str,
    ) -> SplitPreviewResponse:
        job = await canonical_job_registry.get_by_id(session, canonical_job_id)
        if not job:
            raise CanonicalJobNotFoundError(f"Canonical job {canonical_job_id} not found")

        contract = canonical_job_registry.to_contract(job)
        groups = [{"source_id": s.source_id, "provider": s.provider, "url": s.original_url} for s in contract.sources]

        return SplitPreviewResponse(
            source_job_id=job.id,
            source_links=contract.sources,
            proposed_split_groups=groups,
            affected_references_warning=[
                "Any existing matches will remain tied to this original job unless manually re-evaluated."
            ],
        )


split_preview_engine = SplitPreviewEngine()
