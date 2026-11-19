"""Stage 26 Job Discovery Service Integration Bridge (Stage 27)."""

from typing import Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import JobListing
from app.recruitment.aggregation.contracts import AggregationTaskRecord, AggregationTaskType
from app.recruitment.aggregation.processing.incremental import batch_aggregation_processor


class DiscoveryIntegrationBridge:
    """Bridges Stage 26 job listings into Stage 27 canonical aggregation."""

    async def sync_from_job_listings(
        self,
        session: AsyncSession,
        limit: int = 100,
    ) -> AggregationTaskRecord:
        """Load unaggregated Stage 26 JobListings from database and ingest them."""
        stmt = select(JobListing).limit(limit)
        res = await session.execute(stmt)
        listings = res.scalars().all()

        observations = []
        for l in listings:
            observations.append({
                "id": f"obs_listing_{l.id}",
                "listing_id": l.id,
                "source_id": l.source_id,
                "provider": "greenhouse",
                "native_posting_id": l.external_id,
                "title": l.title,
                "employer_name": l.company,
                "source_url": l.application_url,
                "application_url": l.application_url,
                "location_raw": l.location,
                "workplace_type": l.work_arrangement,
                "employment_type": l.employment_type,
                "salary_raw": l.salary_range,
                "description_text": l.description,
            })

        return await batch_aggregation_processor.process_batch(
            session=session,
            observations=observations,
            task_type=AggregationTaskType.SOURCE_SYNC,
        )


discovery_integration_bridge = DiscoveryIntegrationBridge()
