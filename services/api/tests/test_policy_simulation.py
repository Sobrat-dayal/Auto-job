"""Unit tests for Section 114: Policy Simulator, 'What-If' Overrides, and Explanations."""

from decimal import Decimal
import pytest
from app.recruitment.policy.contracts import (
    BlockedEmployerItem,
    CareerStrategy,
    CareerStrategyUpdateRequest,
    CompensationPolicy,
    CompensationUnit,
    EmployerRestrictions,
    JobOpportunityContext,
    PolicyDecisionOutcome,
    PolicySimulationRequest,
    WorkArrangement,
    WorkArrangementPreference,
)
from app.recruitment.policy.simulation.simulator import PolicySimulator
from app.recruitment.profile.contracts import ApplicantProfile, LocationInfo


@pytest.fixture
def sim_strategy() -> CareerStrategy:
    return CareerStrategy(
        id="strat_sim_01",
        title="Simulation Strategy",
        work_arrangement=WorkArrangementPreference(
            allowed_arrangements=[WorkArrangement.REMOTE, WorkArrangement.HYBRID],
            preferred_arrangement=WorkArrangement.REMOTE,
        ),
        compensation=CompensationPolicy(
            currency="USD",
            min_acceptable_amount=Decimal("100000.00"),
        ),
        employers=EmployerRestrictions(
            blocked_employers=[
                BlockedEmployerItem(id="b1", employer_name="BlockedStartup", reason="Hostile culture")
            ]
        ),
    )


def test_simulation_workflow(sim_strategy: CareerStrategy):
    profile = ApplicantProfile(
        id="p_sim",
        owner_id="u_sim",
        display_label="Sim Applicant",
        location=LocationInfo(country="United States"),
    )

    # 1. Evaluate job that meets initial policy
    job = JobOpportunityContext(
        id="job_sim_01",
        title="Backend Engineer",
        employer_name="NormalCorp",
        work_arrangement=WorkArrangement.REMOTE,
        compensation_min=Decimal("120000.00"),
    )

    req1 = PolicySimulationRequest(synthetic_job=job)
    resp1 = PolicySimulator.simulate(req1, strategy=sim_strategy, profile=profile)
    assert resp1.decision.decision == PolicyDecisionOutcome.PROCEED
    assert resp1.decision.overall_score >= 80.0

    # 2. Test 'what-if' override: Change min acceptable salary to $150,000
    req2 = PolicySimulationRequest(
        synthetic_job=job,
        override_policy=CareerStrategyUpdateRequest(
            compensation=CompensationPolicy(
                currency="USD",
                min_acceptable_amount=Decimal("150000.00"),
            )
        ),
    )
    resp2 = PolicySimulator.simulate(req2, strategy=sim_strategy, profile=profile)
    # The offered $120,000 is now below the overridden $150,000 minimum
    assert resp2.decision.decision == PolicyDecisionOutcome.REJECTED_BY_PREFERENCE
    assert "below minimum acceptable" in resp2.decision.explanation

    # 3. Test employer blocklist in simulation
    job_blocked = JobOpportunityContext(
        id="job_sim_02",
        title="Backend Engineer",
        employer_name="BlockedStartup",
        compensation_min=Decimal("130000.00"),
    )
    req3 = PolicySimulationRequest(synthetic_job=job_blocked)
    resp3 = PolicySimulator.simulate(req3, strategy=sim_strategy, profile=profile)
    assert resp3.decision.decision == PolicyDecisionOutcome.PROHIBITED_BY_POLICY
    assert "Hostile culture" in resp3.decision.explanation
