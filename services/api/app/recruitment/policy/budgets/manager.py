"""Multi-Agent Shared Application Budget & Concurrency Controller (Stage 25)."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime
from typing import Optional
from uuid import uuid4
from app.recruitment.policy.contracts import (
    BudgetReservationRequest,
    BudgetReservationResponse,
    RecruitmentBudget,
)
from app.recruitment.policy.errors import BudgetExceededError


class ApplicationBudgetController:
    """Thread-safe, transaction-safe shared application budget controller preventing multi-agent quota overbooking."""

    def __init__(self, initial_budget: Optional[RecruitmentBudget] = None) -> None:
        self._budget = initial_budget or RecruitmentBudget(owner_id="default_user")
        self._lock = asyncio.Lock()
        self._active_reservations: dict[str, dict] = {}

    def get_budget(self) -> RecruitmentBudget:
        return self._budget

    def set_budget(self, budget: RecruitmentBudget) -> None:
        self._budget = budget

    async def reserve_budget(self, req: BudgetReservationRequest) -> BudgetReservationResponse:
        """Atomically reserves an application slot across concurrent agent workers."""
        async with self._lock:
            # Check for date boundary reset
            self._check_period_reset()

            # 1. Global Daily Capacity Check
            if self._budget.remaining_daily <= 0:
                return BudgetReservationResponse(
                    reservation_id="",
                    is_reserved=False,
                    remaining_daily=self._budget.remaining_daily,
                    remaining_weekly=self._budget.remaining_weekly,
                    remaining_monthly=self._budget.remaining_monthly,
                    failure_reason=f"Daily application budget limit reached ({self._budget.max_daily_applications}/day).",
                )

            # 2. Global Weekly Capacity Check
            if self._budget.remaining_weekly <= 0:
                return BudgetReservationResponse(
                    reservation_id="",
                    is_reserved=False,
                    remaining_daily=self._budget.remaining_daily,
                    remaining_weekly=self._budget.remaining_weekly,
                    remaining_monthly=self._budget.remaining_monthly,
                    failure_reason=f"Weekly application budget limit reached ({self._budget.max_weekly_applications}/week).",
                )

            # 3. Global Monthly Capacity Check
            if self._budget.remaining_monthly <= 0:
                return BudgetReservationResponse(
                    reservation_id="",
                    is_reserved=False,
                    remaining_daily=self._budget.remaining_daily,
                    remaining_weekly=self._budget.remaining_weekly,
                    remaining_monthly=self._budget.remaining_monthly,
                    failure_reason=f"Monthly application budget limit reached ({self._budget.max_monthly_applications}/month).",
                )

            # 4. Per-Employer Quota Check
            emp_norm = req.employer.lower().strip()
            current_emp_count = self._budget.employer_counts.get(emp_norm, 0)
            if current_emp_count >= self._budget.max_per_employer_period:
                return BudgetReservationResponse(
                    reservation_id="",
                    is_reserved=False,
                    remaining_daily=self._budget.remaining_daily,
                    remaining_weekly=self._budget.remaining_weekly,
                    remaining_monthly=self._budget.remaining_monthly,
                    failure_reason=f"Per-employer limit reached for '{req.employer}' (Max {self._budget.max_per_employer_period}).",
                )

            # 5. Per-Platform Quota Check
            plat_norm = req.platform.lower().strip()
            current_plat_count = self._budget.platform_counts.get(plat_norm, 0)
            if current_plat_count >= self._budget.max_per_platform_period:
                return BudgetReservationResponse(
                    reservation_id="",
                    is_reserved=False,
                    remaining_daily=self._budget.remaining_daily,
                    remaining_weekly=self._budget.remaining_weekly,
                    remaining_monthly=self._budget.remaining_monthly,
                    failure_reason=f"Per-platform limit reached for '{req.platform}' (Max {self._budget.max_per_platform_period}).",
                )

            # Perform atomic reservation
            res_id = f"res_{uuid4().hex[:10]}"
            self._budget.daily_reserved += 1
            self._active_reservations[res_id] = {
                "job_id": req.job_id,
                "employer": emp_norm,
                "platform": plat_norm,
                "agent_id": req.agent_id,
                "created_at": datetime.now(UTC),
            }

            return BudgetReservationResponse(
                reservation_id=res_id,
                is_reserved=True,
                remaining_daily=self._budget.remaining_daily,
                remaining_weekly=self._budget.remaining_weekly,
                remaining_monthly=self._budget.remaining_monthly,
            )

    async def confirm_reservation(self, reservation_id: str) -> bool:
        """Confirms successful operation, transitioning reserved slot to confirmed usage."""
        async with self._lock:
            info = self._active_reservations.pop(reservation_id, None)
            if not info:
                return False

            if self._budget.daily_reserved > 0:
                self._budget.daily_reserved -= 1

            self._budget.daily_confirmed += 1
            self._budget.weekly_confirmed += 1
            self._budget.monthly_confirmed += 1

            emp = info["employer"]
            plat = info["platform"]
            self._budget.employer_counts[emp] = self._budget.employer_counts.get(emp, 0) + 1
            self._budget.platform_counts[plat] = self._budget.platform_counts.get(plat, 0) + 1

            return True

    async def release_reservation(self, reservation_id: str) -> bool:
        """Safely rolls back an unconsumed reservation (e.g. when a workflow cancels or fails validation)."""
        async with self._lock:
            info = self._active_reservations.pop(reservation_id, None)
            if not info:
                return False

            if self._budget.daily_reserved > 0:
                self._budget.daily_reserved -= 1

            return True

    def _check_period_reset(self) -> None:
        """Resets period counters if date rollovers have elapsed."""
        now = datetime.now(UTC)
        last = self._budget.last_reset_utc

        # Daily reset check
        if now.date() > last.date():
            self._budget.daily_confirmed = 0
            self._budget.daily_reserved = 0
            self._budget.last_reset_utc = now

        # Weekly reset check (every Monday or 7 days)
        if (now - last).days >= 7:
            self._budget.weekly_confirmed = 0
            self._budget.employer_counts.clear()
            self._budget.platform_counts.clear()

        # Monthly reset check
        if now.month != last.month or now.year != last.year:
            self._budget.monthly_confirmed = 0
