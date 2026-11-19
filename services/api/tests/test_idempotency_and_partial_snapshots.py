"""Tests for Idempotency, Partial Snapshot Reconciliation, and Checkpoints (Stage 27)."""

import pytest
from uuid import uuid4
from datetime import UTC, datetime

from sqlalchemy import select
from app.db.engine import async_session_factory
from app.db.models import AggregationCheckpointModel, CanonicalJobModel
from app.recruitment.aggregation.canonical.registry import canonical_job_registry
from app.recruitment.aggregation.canonical.status import reconcile_canonical_status
from app.recruitment.aggregation.contracts import AggregationTaskStatus, CanonicalJobStatus
from app.recruitment.aggregation.processing.incremental import batch_aggregation_processor
from app.recruitment.aggregation.processing.ingestion import observation_ingestion_pipeline


@pytest.mark.asyncio
async def test_idempotent_ingestion():
    """Verify that ingesting the exact same source observation multiple times is strictly idempotent."""
    prefix = uuid4().hex[:6]
    obs_id = f"obs_idemp_{prefix}"
    url = f"https://idempotent.example/jobs/{prefix}"

    async with async_session_factory() as session:
        # Ingest 1st time
        job1, merged1 = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=obs_id,
            source_id="src_lever",
            provider="lever",
            employer_name=f"IdempCorp {prefix}",
            title="Senior Infrastructure Architect",
            source_url=url,
            native_posting_id=f"lev_{prefix}",
            description_text="Leading cloud infrastructure and distributed systems architecture.",
        )
        await session.commit()
        job1_id = job1.id
        assert job1.source_count == 1
        assert merged1 is False

        # Ingest 2nd time (identical observation_id)
        job2, merged2 = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=obs_id,
            source_id="src_lever",
            provider="lever",
            employer_name=f"IdempCorp {prefix}",
            title="Senior Infrastructure Architect",
            source_url=url,
            native_posting_id=f"lev_{prefix}",
            description_text="Leading cloud infrastructure and distributed systems architecture.",
        )
        await session.commit()
        assert job2.id == job1_id
        assert merged2 is False

        # Ingest 3rd time
        job3, merged3 = await observation_ingestion_pipeline.ingest_observation(
            session=session,
            observation_id=obs_id,
            source_id="src_lever",
            provider="lever",
            employer_name=f"IdempCorp {prefix}",
            title="Senior Infrastructure Architect",
            source_url=url,
            native_posting_id=f"lev_{prefix}",
            description_text="Leading cloud infrastructure and distributed systems architecture.",
        )
        await session.commit()
        assert job3.id == job1_id

        # Verify exactly one canonical job exists with this title
        jobs = await canonical_job_registry.list_jobs(session=session, query="Senior Infrastructure Architect")
        matched = [j for j in jobs if j.id == job1_id]
        assert len(matched) == 1
        assert matched[0].source_count == 1


@pytest.mark.asyncio
async def test_partial_snapshot_status_reconciliation():
    """Verify conservative status reconciliation under partial snapshots and network failures."""
    # 1. Partial snapshot: missing items MUST NOT be marked closed
    status_partial = reconcile_canonical_status(
        source_availabilities=[{"availability": "not_in_feed"}],
        is_partial_snapshot=True,
    )
    assert status_partial == CanonicalJobStatus.POSSIBLY_ACTIVE

    # 2. Source network failure / rate limit: do not mark closed
    status_failure = reconcile_canonical_status(
        source_availabilities=[{"availability": "rate_limited"}],
        is_partial_snapshot=False,
    )
    assert status_failure == CanonicalJobStatus.POSSIBLY_ACTIVE

    # 3. Active in at least one source: always active
    status_active = reconcile_canonical_status(
        source_availabilities=[
            {"availability": "closed"},
            {"availability": "available"},
        ],
        is_partial_snapshot=False,
    )
    assert status_active == CanonicalJobStatus.ACTIVE

    # 4. Explicit closure across all sources: marked closed
    status_closed = reconcile_canonical_status(
        source_availabilities=[
            {"availability": "closed"},
            {"availability": "removed"},
        ],
        is_partial_snapshot=False,
    )
    assert status_closed == CanonicalJobStatus.CLOSED


@pytest.mark.asyncio
async def test_batch_checkpointing_workflow():
    """Verify incremental batch aggregation and checkpoint persistence."""
    prefix = uuid4().hex[:6]

    observations = [
        {
            "id": f"obs_{prefix}_1",
            "source_id": "src_gh",
            "provider": "greenhouse",
            "employer_name": f"CheckCorp {prefix}",
            "title": "Systems Engineer",
            "source_url": f"https://check.example/{prefix}/1",
            "native_posting_id": f"req_{prefix}_1",
            "description_text": "Building resilient systems at scale.",
        },
        {
            "id": f"obs_{prefix}_2",
            "source_id": "src_gh",
            "provider": "greenhouse",
            "employer_name": f"CheckCorp {prefix}",
            "title": "Backend Developer",
            "source_url": f"https://check.example/{prefix}/2",
            "native_posting_id": f"req_{prefix}_2",
            "description_text": "Python and FastAPI backend services.",
        },
    ]

    async with async_session_factory() as session:
        task_record = await batch_aggregation_processor.process_batch(
            session=session,
            observations=observations,
        )
        await session.commit()

        assert task_record.observations_total == 2
        assert task_record.observations_processed == 2
        assert task_record.canonical_jobs_created == 2
        assert task_record.status == AggregationTaskStatus.COMPLETED

        # Verify Checkpoint exists in DB
        stmt_cp = select(AggregationCheckpointModel).where(AggregationCheckpointModel.task_id == task_record.id)
        res_cp = await session.execute(stmt_cp)
        checkpoint = res_cp.scalar_one_or_none()
        assert checkpoint is not None
        assert checkpoint.processed_count == 2
        assert checkpoint.last_processed_observation_id == f"obs_{prefix}_2"
