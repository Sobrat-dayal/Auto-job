"""Tests for transactional merge, alias supersession, and split/unmerge operations (Stage 27)."""

import pytest
from uuid import uuid4
from app.db.engine import async_session_factory
from app.recruitment.aggregation.canonical.registry import canonical_job_registry
from app.recruitment.aggregation.canonical.source_links import source_link_manager
from app.recruitment.aggregation.identity_operations.merge import merge_execution_engine
from app.recruitment.aggregation.identity_operations.merge_preview import merge_preview_engine
from app.recruitment.aggregation.identity_operations.split import split_execution_engine
from app.recruitment.aggregation.identity_operations.split_preview import split_preview_engine
from app.recruitment.aggregation.identity_operations.supersession import supersession_manager


@pytest.mark.asyncio
async def test_merge_preview_and_execution():
    """Section 41 & 95: Test merge preview and transactional merge execution."""
    prefix = uuid4().hex[:6]

    async with async_session_factory() as session:
        # Create Job A
        job_a = await canonical_job_registry.create_canonical_job(
            session=session,
            title="Senior Platform Engineer",
            primary_source_id="src_a",
            primary_url=f"https://platform.example/{prefix}/a",
        )
        link_a = await source_link_manager.link_source(
            session=session,
            canonical_job_id=job_a.id,
            source_observation_id=f"obs_a_{prefix}",
            source_id="src_a",
            provider="greenhouse",
            native_posting_id=f"native_a_{prefix}",
            original_url=f"https://platform.example/{prefix}/a",
        )

        # Create Job B
        job_b = await canonical_job_registry.create_canonical_job(
            session=session,
            title="Senior Platform Engineer",
            primary_source_id="src_b",
            primary_url=f"https://platform.example/{prefix}/b",
        )
        link_b = await source_link_manager.link_source(
            session=session,
            canonical_job_id=job_b.id,
            source_observation_id=f"obs_b_{prefix}",
            source_id="src_b",
            provider="lever",
            native_posting_id=f"native_b_{prefix}",
            original_url=f"https://platform.example/{prefix}/b",
        )
        await session.commit()

        # 1. Preview Merge
        prev = await merge_preview_engine.preview_merge(
            session=session,
            surviving_job_id=job_a.id,
            superseded_job_id=job_b.id,
        )
        assert prev.surviving_job_id == job_a.id
        assert prev.superseded_job_id == job_b.id
        assert prev.resulting_source_count == 2
        assert link_b.id in prev.source_links_to_transfer

        # 2. Execute Merge
        res = await merge_execution_engine.execute_merge(
            session=session,
            surviving_job_id=job_a.id,
            superseded_job_id=job_b.id,
            actor="test_user",
            reason="Confirmed exact duplicate vacancy",
        )
        assert res.status == "completed"
        assert res.transferred_source_count == 1
        await session.commit()

        # 3. Verify Alias Supersession: queries for Job B resolve to Job A!
        active_id = await supersession_manager.resolve_active_id(session, job_b.id)
        assert active_id == job_a.id

        # 4. Verify Surviving Job State
        loaded_a = await canonical_job_registry.get_by_id(session, job_a.id)
        assert loaded_a.source_count == 2
        assert loaded_a.version >= 2

        # 5. Verify Superseded Job Marked Closed
        loaded_b = await canonical_job_registry.get_by_id(session, job_b.id)
        assert loaded_b.status == "closed"


@pytest.mark.asyncio
async def test_false_merge_and_split():
    """Section 114: Reversing an erroneous merge through authorized split."""
    prefix = uuid4().hex[:6]

    async with async_session_factory() as session:
        # Create Job with 2 linked sources (as if erroneously merged)
        job = await canonical_job_registry.create_canonical_job(
            session=session,
            title="Lead QA Engineer",
            primary_source_id="src_1",
            primary_url=f"https://qa.example/{prefix}/1",
        )
        link1 = await source_link_manager.link_source(
            session=session,
            canonical_job_id=job.id,
            source_observation_id=f"obs_1_{prefix}",
            source_id="src_1",
            provider="greenhouse",
            native_posting_id=f"id_1_{prefix}",
            original_url=f"https://qa.example/{prefix}/1",
        )
        link2 = await source_link_manager.link_source(
            session=session,
            canonical_job_id=job.id,
            source_observation_id=f"obs_2_{prefix}",
            source_id="src_2",
            provider="ashby",
            native_posting_id=f"id_2_{prefix}",
            original_url=f"https://qa.example/{prefix}/2",
        )
        job.source_count = 2
        await session.commit()

        # Preview Split
        prev = await split_preview_engine.preview_split(session, job.id)
        assert len(prev.source_links) == 2

        # Execute Split: detach link2 into new canonical job
        split_res = await split_execution_engine.execute_split(
            session=session,
            source_job_id=job.id,
            source_link_ids_to_detach=[link2.id],
            actor="test_admin",
            reason="Different projects and hiring managers",
        )
        assert split_res.status == "completed"
        assert len(split_res.new_canonical_job_ids) == 1
        new_job_id = split_res.new_canonical_job_ids[0]
        await session.commit()

        # Verify Original Job has 1 source
        orig_loaded = await canonical_job_registry.get_by_id(session, job.id)
        assert orig_loaded.source_count == 1
        orig_contract = canonical_job_registry.to_contract(orig_loaded)
        assert len(orig_contract.sources) == 1
        assert orig_contract.sources[0].id == link1.id

        # Verify New Job has detached source
        new_loaded = await canonical_job_registry.get_by_id(session, new_job_id)
        assert new_loaded.source_count == 1
        new_contract = canonical_job_registry.to_contract(new_loaded)
        assert len(new_contract.sources) == 1
        assert new_contract.sources[0].id == link2.id
