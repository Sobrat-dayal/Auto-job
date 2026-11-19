"""Rate limiting and resource budget controller."""

from __future__ import annotations

import asyncio
from datetime import UTC, datetime, timedelta
import logging
from typing import Optional
from app.recruitment.monitoring.errors import QuotaExceededError, WatchRateLimitedError

logger = logging.getLogger("autonom.recruitment.monitoring.execution.budgets")


class BudgetController:
    """Manages request budgets, provider cooldowns, and global concurrency."""

    def __init__(self, global_concurrency_limit: int = 3, daily_request_budget: int = 500) -> None:
        self.global_concurrency_limit = global_concurrency_limit
        self.daily_request_budget = daily_request_budget
        self._active_runs: int = 0
        self._daily_requests_used: int = 0
        self._budget_reset_date = datetime.now(UTC).date()
        self._provider_cooldowns: dict[str, datetime] = {}
        self._lock = asyncio.Lock()

    async def check_and_reserve_run(self, source_count: int = 1) -> None:
        """Verifies capacity before initiating a monitoring run."""
        async with self._lock:
            # Check date rollover
            today = datetime.now(UTC).date()
            if today > self._budget_reset_date:
                self._daily_requests_used = 0
                self._budget_reset_date = today

            if self._active_runs >= self.global_concurrency_limit:
                raise QuotaExceededError(
                    f"Global concurrency limit reached ({self._active_runs}/{self.global_concurrency_limit})."
                )

            estimated_cost = source_count * 3
            if self._daily_requests_used + estimated_cost > self.daily_request_budget:
                raise QuotaExceededError(
                    f"Daily request budget exhausted ({self._daily_requests_used}/{self.daily_request_budget})."
                )

            self._active_runs += 1
            self._daily_requests_used += estimated_cost

    async def release_run(self) -> None:
        """Decrements active run count upon completion."""
        async with self._lock:
            self._active_runs = max(0, self._active_runs - 1)

    def record_cooldown(self, source_or_provider: str, retry_after_seconds: int = 300) -> None:
        """Records a provider rate limit cooldown."""
        until = datetime.now(UTC) + timedelta(seconds=retry_after_seconds)
        self._provider_cooldowns[source_or_provider] = until
        logger.warning(f"Recorded cooldown for provider '{source_or_provider}' until {until.isoformat()}")

    def is_in_cooldown(self, source_or_provider: str) -> bool:
        """Checks if a provider or source is currently rate limited."""
        until = self._provider_cooldowns.get(source_or_provider)
        if not until:
            return False
        if until > datetime.now(UTC):
            return True
        # Expired
        del self._provider_cooldowns[source_or_provider]
        return False

    def get_cooldown_remaining(self, source_or_provider: str) -> Optional[int]:
        """Returns seconds remaining on cooldown if active."""
        until = self._provider_cooldowns.get(source_or_provider)
        if not until:
            return None
        diff = (until - datetime.now(UTC)).total_seconds()
        return max(0, int(diff)) if diff > 0 else None

    def get_all_cooldowns(self) -> list[dict[str, Any]]:
        now = datetime.now(UTC)
        res = []
        for k, v in list(self._provider_cooldowns.items()):
            if v > now:
                res.append({"provider": k, "until": v.isoformat(), "seconds_remaining": int((v - now).total_seconds())})
        return res


budget_controller = BudgetController()
