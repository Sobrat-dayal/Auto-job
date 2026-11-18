"""Zero-Side-Effect Recruitment Policy Simulator (Stage 25)."""

from __future__ import annotations

from typing import Optional
from app.recruitment.policy.contracts import (
    CareerStrategy,
    JobOpportunityContext,
    PolicySimulationRequest,
    PolicySimulationResponse,
)
from app.recruitment.policy.eligibility.evaluator import JobEligibilityEvaluator
from app.recruitment.policy.rules.engine import PolicyRulesEngine
from app.recruitment.profile.contracts import ApplicantProfile


class PolicySimulator:
    """Executes hypothetical policy simulations against arbitrary job opportunities with guaranteed zero side-effects."""

    @classmethod
    def simulate(
        cls,
        req: PolicySimulationRequest,
        strategy: CareerStrategy,
        profile: ApplicantProfile,
        is_emergency_stop_active: bool = False,
    ) -> PolicySimulationResponse:
        # Clone strategy if override is provided for 'what-if' testing
        target_strategy = strategy
        if req.override_policy:
            update_data = req.override_policy.model_dump(exclude_unset=True)
            # Create a modified copy
            strategy_dict = target_strategy.model_dump()
            strategy_dict.update(update_data)
            target_strategy = CareerStrategy(**strategy_dict)

        # 1. Detect conflicts on active or overridden policy
        conflicts = PolicyRulesEngine.detect_conflicts(target_strategy)

        # 2. Evaluate eligibility against canonical profile facts
        eligibility = JobEligibilityEvaluator.evaluate_eligibility(
            profile=profile,
            job=req.synthetic_job,
        )

        # 3. Evaluate deterministic policy rules and precedence
        decision = PolicyRulesEngine.evaluate_decision(
            strategy=target_strategy,
            job=req.synthetic_job,
            eligibility=eligibility,
            is_emergency_stop_active=is_emergency_stop_active,
        )

        simulation_notes = (
            f"Simulation executed against Strategy '{target_strategy.title}'. "
            f"Evaluated {len(eligibility.categories)} eligibility categories and {len(decision.hard_constraints)} hard constraints."
        )

        return PolicySimulationResponse(
            decision=decision,
            strategy_title=target_strategy.title,
            policy_version=1,
            detected_conflicts=conflicts,
            simulation_notes=simulation_notes,
        )
