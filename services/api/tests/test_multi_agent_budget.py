"""Concurrent multi-agent tests for Section 111: Shared Application Budget and Quota Controller."""

import asyncio
import pytest
from app.recruitment.policy.budgets.manager import ApplicationBudgetController
from app.recruitment.policy.contracts import (
    BudgetReservationRequest,
    RecruitmentBudget,
)


@pytest.mark.asyncio
async def test_concurrent_multi_agent_budget_reservations():
    """Verify that multiple concurrent agent workers share a single atomic daily budget without overbooking."""
    # Shared daily budget of 5 applications
    shared_budget = RecruitmentBudget(
        owner_id="user_01",
        max_daily_applications=5,
        max_weekly_applications=20,
        max_monthly_applications=50,
        max_per_employer_period=2,
    )
    controller = ApplicationBudgetController(initial_budget=shared_budget)

    # 3 agents attempting 3 requests each (total 9 requests, only 5 can succeed)
    async def worker_attempt(agent_name: str, task_idx: int) -> bool:
        req = BudgetReservationRequest(
            job_id=f"job_{agent_name}_{task_idx}",
            employer=f"Company_{task_idx}",
            platform="greenhouse",
            agent_id=agent_name,
        )
        res = await controller.reserve_budget(req)
        return res.is_reserved

    tasks = [
        worker_attempt("agent_alpha", 1),
        worker_attempt("agent_alpha", 2),
        worker_attempt("agent_alpha", 3),
        worker_attempt("agent_beta", 1),
        worker_attempt("agent_beta", 2),
        worker_attempt("agent_beta", 3),
        worker_attempt("agent_gamma", 1),
        worker_attempt("agent_gamma", 2),
        worker_attempt("agent_gamma", 3),
    ]

    results = await asyncio.gather(*tasks)
    successful_reservations = sum(1 for r in results if r is True)
    failed_reservations = sum(1 for r in results if r is False)

    # Exactly 5 must succeed, exactly 4 must fail due to atomic capacity exhaustion
    assert successful_reservations == 5
    assert failed_reservations == 4
    assert controller.get_budget().remaining_daily == 0


@pytest.mark.asyncio
async def test_budget_reservation_confirm_and_release():
    shared_budget = RecruitmentBudget(
        owner_id="user_01",
        max_daily_applications=3,
        max_per_employer_period=1,
    )
    controller = ApplicationBudgetController(initial_budget=shared_budget)

    # 1. Reserve slot for Stripe
    req1 = BudgetReservationRequest(job_id="j1", employer="Stripe", platform="lever", agent_id="agent_1")
    res1 = await controller.reserve_budget(req1)
    assert res1.is_reserved is True
    assert controller.get_budget().daily_reserved == 1
    assert controller.get_budget().remaining_daily == 2

    # 2. Confirm reservation
    confirmed = await controller.confirm_reservation(res1.reservation_id)
    assert confirmed is True
    assert controller.get_budget().daily_reserved == 0
    assert controller.get_budget().daily_confirmed == 1
    assert controller.get_budget().remaining_daily == 2

    # 3. Second application to same employer should fail per-employer limit (max 1)
    req2 = BudgetReservationRequest(job_id="j2", employer="Stripe", platform="lever", agent_id="agent_2")
    res2 = await controller.reserve_budget(req2)
    assert res2.is_reserved is False
    assert "Per-employer limit reached" in res2.failure_reason

    # 4. Reserve another slot for Netflix and release it (cancellation)
    req3 = BudgetReservationRequest(job_id="j3", employer="Netflix", platform="workday", agent_id="agent_3")
    res3 = await controller.reserve_budget(req3)
    assert res3.is_reserved is True
    assert controller.get_budget().daily_reserved == 1

    released = await controller.release_reservation(res3.reservation_id)
    assert released is True
    assert controller.get_budget().daily_reserved == 0
    # Capacity is restored
    assert controller.get_budget().remaining_daily == 2
