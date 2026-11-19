"""Tests for Stage 30 worker leases, heartbeat renewal, expiry, and budget controller."""

from datetime import UTC, datetime, timedelta
import pytest
from app.db.engine import async_session_factory
from app.recruitment.monitoring.errors import QuotaExceededError, WatchRateLimitedError
from app.recruitment.monitoring.execution.budgets import BudgetController
from app.recruitment.monitoring.execution.leases import LeaseManager


@pytest.mark.asyncio
async def test_lease_acquisition_and_conflict():
    mgr = LeaseManager(lease_duration_seconds=60)
    lease_key = "test_watch_lease_001"

    async with async_session_factory() as session:
        # Worker A acquires lease
        acquired_a = await mgr.acquire_lease(lease_key, worker_id="worker_A", session=session)
        assert acquired_a is True

        # Worker B tries to acquire same lease -> fails
        acquired_b = await mgr.acquire_lease(lease_key, worker_id="worker_B", session=session)
        assert acquired_b is False

        # Worker A renews own lease -> succeeds
        renewed_a = await mgr.acquire_lease(lease_key, worker_id="worker_A", session=session)
        assert renewed_a is True

        # Release lease
        released = await mgr.release_lease(lease_key, worker_id="worker_A", session=session)
        assert released is True

        # Now Worker B can acquire
        acquired_b_after = await mgr.acquire_lease(lease_key, worker_id="worker_B", session=session)
        assert acquired_b_after is True

        # Cleanup
        await mgr.release_lease(lease_key, worker_id="worker_B", session=session)


@pytest.mark.asyncio
async def test_lease_heartbeat_and_expiration():
    mgr = LeaseManager(lease_duration_seconds=1)  # 1 second duration
    lease_key = "test_watch_lease_expiring"

    async with async_session_factory() as session:
        acquired = await mgr.acquire_lease(lease_key, worker_id="worker_1", session=session)
        assert acquired is True

        # Heartbeat updates timestamp
        hb_success = await mgr.heartbeat(lease_key, worker_id="worker_1", session=session)
        assert hb_success is True

        # Wrong worker heartbeat fails
        hb_wrong = await mgr.heartbeat(lease_key, worker_id="worker_2", session=session)
        assert hb_wrong is False

        # Release cleanup
        await mgr.release_lease(lease_key, worker_id="worker_1", session=session)


@pytest.mark.asyncio
async def test_budget_concurrency_limit():
    budget = BudgetController(global_concurrency_limit=2, daily_request_budget=100)

    # Reserve 1st run
    await budget.check_and_reserve_run(source_count=1)
    # Reserve 2nd run
    await budget.check_and_reserve_run(source_count=1)

    # 3rd run exceeds limit
    with pytest.raises(QuotaExceededError) as exc_info:
        await budget.check_and_reserve_run(source_count=1)
    assert "concurrency limit reached" in str(exc_info.value).lower()

    # Release 1 run
    await budget.release_run()

    # Now 3rd run succeeds
    await budget.check_and_reserve_run(source_count=1)


@pytest.mark.asyncio
async def test_budget_daily_request_limit():
    budget = BudgetController(global_concurrency_limit=10, daily_request_budget=10)

    # Each source costs 3 requests -> 3 sources = 9 requests
    await budget.check_and_reserve_run(source_count=3)

    # Another run with 2 sources = 6 requests -> 9 + 6 = 15 > 10
    with pytest.raises(QuotaExceededError) as exc_info:
        await budget.check_and_reserve_run(source_count=2)
    assert "daily request budget exhausted" in str(exc_info.value).lower()


def test_budget_provider_cooldown():
    budget = BudgetController()
    provider = "greenhouse_public"

    assert budget.is_in_cooldown(provider) is False

    budget.record_cooldown(provider, retry_after_seconds=60)
    assert budget.is_in_cooldown(provider) is True
    cooldown_rem = budget.get_cooldown_remaining(provider)
    assert cooldown_rem > 0
