"""Recruitment Policy Multi-Agent Integration Adapter (Stage 25)."""

from __future__ import annotations

from typing import Any, Optional
from app.recruitment.policy.contracts import (
    JobOpportunityContext,
    RecruitmentDecision,
)
from app.recruitment.profile.contracts import ApplicantProfile


class RecruitmentPolicyAgentAdapter:
    """Provides high-level programmatic interfaces for recruitment agents (Supervisor, Discovery,
    Matching, Application, Verification, and Recovery) to inspect policies and evaluate permissions.
    """

    def __init__(self, policy_service: Any) -> None:
        self.policy_service = policy_service

    def get_agent_policy_snapshot(self, profile_id: Optional[str] = None) -> dict[str, Any]:
        """Assembles a lightweight, structured policy summary for specialist agent prompt context."""
        strategy = self.policy_service.get_active_strategy(profile_id=profile_id)
        budget = self.policy_service.budget_controller.get_budget()

        if not strategy:
            return {
                "active_strategy": None,
                "status": "no_active_strategy",
                "autonomy_mode": "research_only",
                "remaining_daily_budget": budget.remaining_daily,
            }

        return {
            "active_strategy": {
                "id": strategy.id,
                "title": strategy.title,
                "autonomy_mode": strategy.autonomy_mode.value,
                "target_roles": [r.title for r in strategy.target_roles if not r.is_excluded],
                "excluded_roles": [r.title for r in strategy.target_roles if r.is_excluded],
                "allowed_work_arrangements": [a.value for a in strategy.work_arrangement.allowed_arrangements],
                "is_remote_only": (
                    strategy.work_arrangement.is_hard_constraint
                    and len(strategy.work_arrangement.allowed_arrangements) == 1
                    and strategy.work_arrangement.allowed_arrangements[0].value == "remote"
                ),
                "min_acceptable_salary": f"{strategy.compensation.currency} {strategy.compensation.min_acceptable_amount:,.2f}",
                "preferred_salary_range": f"{strategy.compensation.currency} {strategy.compensation.preferred_min:,.2f} - {strategy.compensation.preferred_max or 'unlimited'}",
                "blocked_employers_count": len(strategy.employers.blocked_employers),
                "strict_allowlist_active": strategy.employers.allowlist_mode.value == "strict_allowlist",
                "allowed_employers_count": len(strategy.employers.allowed_employers),
            },
            "remaining_daily_budget": budget.remaining_daily,
            "remaining_weekly_budget": budget.remaining_weekly,
            "pending_reviews_count": len(self.policy_service.autonomy_controller.get_review_queue(status="pending")),
        }

    async def evaluate_job_for_agents(
        self,
        job: JobOpportunityContext,
        strategy_id: Optional[str] = None,
        profile_id: Optional[str] = None,
    ) -> RecruitmentDecision:
        """Invoked by the Job Matching Agent and Supervisor to evaluate suitability and eligibility."""
        return await self.policy_service.evaluate_job(job=job, strategy_id=strategy_id, profile_id=profile_id)

    def check_action_permission(
        self,
        agent_role: str,
        action: str,
        employer: Optional[str] = None,
        platform: Optional[str] = None,
        grant_id: Optional[str] = None,
    ) -> tuple[bool, str]:
        """Invoked by specialist agents before initiating document preparation or workflow execution."""
        strategy = self.policy_service.get_active_strategy()
        mode = strategy.autonomy_mode if strategy else None
        if not mode:
            return False, "No active career strategy found; actions default to prohibited."

        return self.policy_service.autonomy_controller.validate_action_authorization(
            mode=mode,
            action=action,
            grant_id=grant_id,
            employer=employer,
            platform=platform,
        )
