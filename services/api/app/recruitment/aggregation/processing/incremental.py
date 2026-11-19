"""Incremental and Batch Aggregation Processor (Stage 27)."""

from datetime import UTC, datetime
from typing import Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import AggregationCheckpointModel, AggregationErrorModel, AggregationTaskModel
from app.recruitment.aggregation.contracts import (
    AggregationTaskRecord,
    AggregationTaskStatus,
    AggregationTaskType,
)
from app.recruitment.aggregation.processing.ingestion import observation_ingestion_pipeline


class BatchAggregationProcessor:
    """Coordinates batch ingestion with progress tracking, errors, and checkpoints."""

    async def process_batch(
        self,
        session: AsyncSession,
        observations: list[dict[str, Any]],
        task_type: AggregationTaskType = AggregationTaskType.INCREMENTAL,
        auto_merge_enabled: bool = True,
    ) -> AggregationTaskRecord:
        task = AggregationTaskModel(
            task_type=task_type.value,
            status=AggregationTaskStatus.RUNNING.value,
            observations_total=len(observations),
            started_at=datetime.now(UTC),
            created_at=datetime.now(UTC),
        )
        session.add(task)
        await session.flush()

        checkpoint = AggregationCheckpointModel(
            task_id=task.id,
            processed_count=0,
            state_json={},
            updated_at=datetime.now(UTC),
        )
        session.add(checkpoint)
        await session.flush()

        created_count = 0
        merged_count = 0

        for obs in observations:
            obs_id = obs.get("id") or obs.get("observation_id") or "obs_unknown"
            try:
                job, was_merged = await observation_ingestion_pipeline.ingest_observation(
                    session=session,
                    observation_id=obs_id,
                    source_id=obs.get("source_id", "src_default"),
                    provider=obs.get("provider", "greenhouse"),
                    native_posting_id=obs.get("native_posting_id", obs_id),
                    title=obs.get("title", "Untitled Job"),
                    employer_name=obs.get("employer_name", obs.get("employer", "Unknown Employer")),
                    source_url=obs.get("source_url", ""),
                    application_url=obs.get("application_url"),
                    location_raw=obs.get("location_raw") or obs.get("location"),
                    workplace_type=obs.get("workplace_type"),
                    employment_type=obs.get("employment_type"),
                    salary_raw=obs.get("salary_raw") or obs.get("salary_range"),
                    description_text=obs.get("description_text") or obs.get("description"),
                    posted_at=obs.get("posted_at"),
                    listing_id=obs.get("listing_id"),
                    auto_merge_enabled=auto_merge_enabled,
                )

                if was_merged:
                    merged_count += 1
                else:
                    created_count += 1

                task.observations_processed += 1
                checkpoint.processed_count += 1
                checkpoint.last_processed_observation_id = obs_id

            except Exception as e:
                err = AggregationErrorModel(
                    task_id=task.id,
                    observation_id=obs_id,
                    error_type=type(e).__name__,
                    message=str(e),
                )
                session.add(err)

        task.canonical_jobs_created = created_count
        task.merges_performed = merged_count
        task.status = AggregationTaskStatus.COMPLETED.value
        task.completed_at = datetime.now(UTC)
        await session.flush()

        return AggregationTaskRecord(
            id=task.id,
            task_type=task_type,
            status=AggregationTaskStatus.COMPLETED,
            observations_total=task.observations_total,
            observations_processed=task.observations_processed,
            canonical_jobs_created=created_count,
            canonical_jobs_updated=0,
            duplicates_found=merged_count,
            merges_performed=merged_count,
            reviews_queued=0,
            conflicts_detected=0,
            started_at=task.started_at.isoformat() if task.started_at else None,
            completed_at=task.completed_at.isoformat() if task.completed_at else None,
            created_at=task.created_at.isoformat(),
        )


batch_aggregation_processor = BatchAggregationProcessor()
