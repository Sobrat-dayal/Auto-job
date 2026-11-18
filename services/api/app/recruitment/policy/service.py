"""Master Recruitment Policy & Career Preferences Service (Stage 25)."""

from __future__ import annotations

import logging
from decimal import Decimal
from typing import Any, Optional
from uuid import uuid4
from app.core.security import AuthContext
from app.recruitment.policy.autonomy.controller import AutonomyController
from app.recruitment.policy.budgets.manager import ApplicationBudgetController
from app.recruitment.policy.contracts import (
    AllowlistMode,
    AutonomyMode,
    BlockedEmployerItem,
    CareerPreferenceProfile,
    CareerStrategy,
    CareerStrategyCreateRequest,
    CareerStrategyUpdateRequest,
    CompanySize,
    CompensationPolicy,
    CompensationUnit,
    EmployerRestrictions,
    EmploymentType,
    GeographicPreference,
    JobOpportunityContext,
    PolicyDecisionOutcome,
    PolicySimulationRequest,
    PolicySimulationResponse,
    RecruitmentBudget,
    RecruitmentDecision,
    RelocationPreference,
    RoleFamily,
    SeniorityLevel,
    SeniorityPreference,
    SourceRestrictions,
    StandingGrantRecord,
    TargetRoleItem,
    UndisclosedSalaryHandling,
    WorkArrangement,
    WorkArrangementPreference,
)
from app.recruitment.policy.eligibility.evaluator import JobEligibilityEvaluator
from app.recruitment.policy.errors import (
    CareerProfileNotFoundError,
    StrategyNotFoundError,
)
from app.recruitment.policy.integrations.agents import RecruitmentPolicyAgentAdapter
from app.recruitment.policy.lifecycle.versions import PolicyVersionManager
from app.recruitment.policy.rules.engine import PolicyRulesEngine
from app.recruitment.policy.simulation.simulator import PolicySimulator
from app.recruitment.profile.contracts import ApplicantProfile
from app.recruitment.profile.service import applicant_profile_service

logger = logging.getLogger("autonom.recruitment.policy.service")


class RecruitmentPolicyService:
    """Singleton service orchestrator for career preferences, recruitment eligibility,
    policy evaluation, multi-agent budgets, and autonomy governance."""

    def __init__(self) -> None:
        self.budget_controller = ApplicationBudgetController()
        self.autonomy_controller = AutonomyController()
        self.version_manager = PolicyVersionManager()
        self.agent_adapter = RecruitmentPolicyAgentAdapter(self)

        self._profiles: dict[str, CareerPreferenceProfile] = {}
        self._strategies: dict[str, CareerStrategy] = {}
        self._decisions_log: dict[str, RecruitmentDecision] = {}
        self._emergency_stop_active = False

        self._init_samples()

    def _init_samples(self) -> None:
        """Seeds realistic initial career strategies for local operation and testing."""
        strat_backend = CareerStrategy(
            id="strat_backend_01",
            owner_id="default_user",
            profile_id="prof_primary_applicant",
            title="Backend & Distributed Systems Focus",
            description="Core focus on high-throughput backend services, distributed systems, and API architecture in Python/Rust/Go.",
            is_active=True,
            target_roles=[
                TargetRoleItem(
                    id="role_01",
                    title="Backend Engineer",
                    role_family=RoleFamily.BACKEND,
                    seniority=SeniorityLevel.MID_LEVEL,
                    priority=1,
                    alternate_titles=["Software Engineer - Backend", "Server Engineer", "Platform Engineer"],
                ),
                TargetRoleItem(
                    id="role_02",
                    title="Distributed Systems Engineer",
                    role_family=RoleFamily.SYSTEMS,
                    seniority=SeniorityLevel.MID_LEVEL,
                    priority=1,
                ),
                TargetRoleItem(
                    id="role_03",
                    title="Senior Engineering Manager",
                    role_family=RoleFamily.BACKEND,
                    seniority=SeniorityLevel.MANAGEMENT,
                    is_excluded=True,
                    priority=10,
                ),
            ],
            seniority=SeniorityPreference(
                allowed_levels=[SeniorityLevel.ENTRY_LEVEL, SeniorityLevel.JUNIOR, SeniorityLevel.MID_LEVEL, SeniorityLevel.SENIOR],
                min_years=0.0,
                max_years=6.0,
            ),
            employment_types=[EmploymentType.FULL_TIME, EmploymentType.CONTRACT],
            work_arrangement=WorkArrangementPreference(
                allowed_arrangements=[WorkArrangement.REMOTE, WorkArrangement.HYBRID],
                preferred_arrangement=WorkArrangement.REMOTE,
                is_hard_constraint=False,
            ),
            geography=GeographicPreference(
                country="United States",
                allowed_countries=["United States", "Canada"],
                allowed_cities=["San Francisco", "New York", "Seattle", "Austin"],
                excluded_locations=["Miami"],
                remote_within_country_only=True,
                relocation=RelocationPreference.CONDITIONAL,
                preferred_time_zone="America/New_York",
                max_hour_offset=3,
                min_overlap_hours=4,
            ),
            compensation=CompensationPolicy(
                currency="USD",
                unit=CompensationUnit.ANNUAL,
                min_acceptable_amount=Decimal("90000.00"),
                preferred_min=Decimal("120000.00"),
                preferred_max=Decimal("170000.00"),
                undisclosed_handling=UndisclosedSalaryHandling.REQUIRE_REVIEW,
                is_hard_minimum=True,
            ),
            employers=EmployerRestrictions(
                allowlist_mode=AllowlistMode.NO_ALLOWLIST,
                allowed_employers=["Stripe", "Datadog", "GitHub", "Vercel"],
                blocked_employers=[
                    BlockedEmployerItem(
                        id="blk_01",
                        employer_name="SpamCorp Global",
                        domain="spamcorpglobal.com",
                        reason="Unverified offshore recruiting agency with misleading contracts",
                    ),
                    BlockedEmployerItem(
                        id="blk_02",
                        employer_name="Predatory Solutions Inc",
                        domain="predatorysol.io",
                        reason="Unpaid trial assignments and IP forfeiture clauses",
                    ),
                ],
                company_sizes=[CompanySize.STARTUP, CompanySize.MEDIUM_ENTERPRISE, CompanySize.LARGE_ENTERPRISE],
                preferred_industries=["Software", "Developer Tools", "Financial Technology", "Cloud Infrastructure"],
            ),
            sources=SourceRestrictions(
                allowed_sources=["company_website", "greenhouse", "lever", "workday", "ashby"],
                blocked_sources=["shady_aggregator_network"],
            ),
            autonomy_mode=AutonomyMode.PREPARE_AND_REVIEW,
        )

        strat_aiml = CareerStrategy(
            id="strat_aiml_02",
            owner_id="default_user",
            profile_id="prof_primary_applicant",
            title="AI & Machine Learning Engineering",
            description="Focus on applied deep learning, LLM systems, RAG architecture, and inference optimization.",
            is_active=False,
            target_roles=[
                TargetRoleItem(
                    id="role_ml_01",
                    title="Machine Learning Engineer",
                    role_family=RoleFamily.AI_ML,
                    seniority=SeniorityLevel.MID_LEVEL,
                    priority=1,
                ),
                TargetRoleItem(
                    id="role_ml_02",
                    title="AI Systems Architect",
                    role_family=RoleFamily.AI_ML,
                    seniority=SeniorityLevel.SENIOR,
                    priority=2,
                ),
            ],
            compensation=CompensationPolicy(
                currency="USD",
                unit=CompensationUnit.ANNUAL,
                min_acceptable_amount=Decimal("110000.00"),
                preferred_min=Decimal("140000.00"),
                preferred_max=Decimal("200000.00"),
            ),
            autonomy_mode=AutonomyMode.PREAUTHORIZED_PREPARATION,
        )

        self._strategies[strat_backend.id] = strat_backend
        self._strategies[strat_aiml.id] = strat_aiml

        # Create career profile container
        cprof = CareerPreferenceProfile(
            id="cprof_primary",
            owner_id="default_user",
            applicant_profile_id="prof_primary_applicant",
            active_strategy_id=strat_backend.id,
            strategies=[strat_backend, strat_aiml],
            version=1,
        )
        self._profiles[cprof.id] = cprof

        # Create initial snapshot
        self.version_manager.create_snapshot(strat_backend, changelog="Initial system seeding.")

        # Seed sample grant
        self.autonomy_controller.create_grant(
            grantee_agent="application_agent",
            action_type="recruitment.application.prepare",
            max_operations=50,
            validity_days=30,
        )

    # -------------------------------------------------------------------------
    # Emergency Stop Integration
    # -------------------------------------------------------------------------
    def set_emergency_stop(self, is_active: bool) -> None:
        self._emergency_stop_active = is_active

    def is_emergency_stop_active(self) -> bool:
        # Check internal state and Stage 14 emergency service if present
        return self._emergency_stop_active

    # -------------------------------------------------------------------------
    # Career Profile & Strategy Management
    # -------------------------------------------------------------------------
    def get_career_profile(self, profile_id: str) -> Optional[CareerPreferenceProfile]:
        for cp in self._profiles.values():
            if cp.id == profile_id or cp.applicant_profile_id == profile_id:
                return cp
        # Fallback to default
        if self._profiles:
            return next(iter(self._profiles.values()))
        return None

    def list_strategies(self, profile_id: Optional[str] = None) -> list[CareerStrategy]:
        return list(self._strategies.values())

    def get_strategy(self, strategy_id: str) -> Optional[CareerStrategy]:
        return self._strategies.get(strategy_id)

    def get_active_strategy(self, profile_id: Optional[str] = None) -> Optional[CareerStrategy]:
        for s in self._strategies.values():
            if s.is_active:
                return s
        return next(iter(self._strategies.values())) if self._strategies else None

    def create_strategy(self, req: CareerStrategyCreateRequest, auth_context: Optional[AuthContext] = None) -> CareerStrategy:
        strat = CareerStrategy(
            id=f"strat_{uuid4().hex[:8]}",
            owner_id=getattr(auth_context, "client_id", getattr(auth_context, "user_id", "default_user")) if auth_context else "default_user",
            title=req.title,
            description=req.description,
            is_active=req.is_active,
            target_roles=req.target_roles,
            seniority=req.seniority or SeniorityPreference(),
            employment_types=req.employment_types or [EmploymentType.FULL_TIME],
            work_arrangement=req.work_arrangement or WorkArrangementPreference(),
            geography=req.geography or GeographicPreference(),
            compensation=req.compensation or CompensationPolicy(),
            employers=req.employers or EmployerRestrictions(),
            sources=req.sources or SourceRestrictions(),
            max_posting_age_days=req.max_posting_age_days,
            autonomy_mode=req.autonomy_mode,
        )

        if strat.is_active:
            for other in self._strategies.values():
                other.is_active = False

        self._strategies[strat.id] = strat
        self.version_manager.create_snapshot(strat, changelog=f"Created strategy '{strat.title}'")
        return strat

    def update_strategy(self, strategy_id: str, req: CareerStrategyUpdateRequest, auth_context: Optional[AuthContext] = None) -> CareerStrategy:
        strat = self._strategies.get(strategy_id)
        if not strat:
            raise StrategyNotFoundError(strategy_id)

        update_dict = req.model_dump(exclude_unset=True)
        if update_dict.get("is_active"):
            for other in self._strategies.values():
                other.is_active = False

        for k, v in update_dict.items():
            setattr(strat, k, v)

        self.version_manager.create_snapshot(strat, changelog=f"Updated strategy '{strat.title}'")
        return strat

    def activate_strategy(self, strategy_id: str) -> CareerStrategy:
        target = self._strategies.get(strategy_id)
        if not target:
            raise StrategyNotFoundError(strategy_id)

        for s in self._strategies.values():
            s.is_active = (s.id == strategy_id)

        self.version_manager.create_snapshot(target, changelog=f"Activated strategy '{target.title}'")
        return target

    def delete_strategy(self, strategy_id: str) -> bool:
        if strategy_id in self._strategies:
            del self._strategies[strategy_id]
            return True
        return False

    # -------------------------------------------------------------------------
    # Evaluation & Simulation
    # -------------------------------------------------------------------------
    async def evaluate_job(
        self,
        job: JobOpportunityContext,
        strategy_id: Optional[str] = None,
        profile_id: Optional[str] = None,
    ) -> RecruitmentDecision:
        strategy = self._strategies.get(strategy_id) if strategy_id else self.get_active_strategy(profile_id)
        if not strategy:
            raise StrategyNotFoundError(strategy_id or "active")

        # Resolve canonical applicant profile
        profile = applicant_profile_service.get_profile(profile_id or "prof_primary_applicant")
        if not profile:
            # Fallback synthetic profile for tests
            profile = ApplicantProfile(
                id=profile_id or "prof_test",
                owner_id="usr_test",
                display_label="Test Applicant",
            )

        # 1. Deterministic Eligibility Check
        eligibility = JobEligibilityEvaluator.evaluate_eligibility(profile=profile, job=job)

        # 2. Deterministic Rule & Precedence Evaluation
        decision = PolicyRulesEngine.evaluate_decision(
            strategy=strategy,
            job=job,
            eligibility=eligibility,
            is_emergency_stop_active=self.is_emergency_stop_active(),
        )

        # If review is triggered, register in review queue
        if decision.decision == PolicyDecisionOutcome.NEEDS_REVIEW:
            for trigger in decision.review_triggers:
                self.autonomy_controller.add_to_review_queue(
                    job_id=job.id,
                    job_title=job.title,
                    employer=job.employer_name,
                    trigger=trigger,
                    reason=decision.explanation,
                    is_mandatory=True,
                )

        self._decisions_log[decision.id] = decision
        return decision

    def simulate_policy(self, req: PolicySimulationRequest) -> PolicySimulationResponse:
        strategy = self._strategies.get(req.strategy_id) if req.strategy_id else self.get_active_strategy(req.profile_id)
        if not strategy:
            raise StrategyNotFoundError(req.strategy_id or "active")

        profile = applicant_profile_service.get_profile(req.profile_id or "prof_primary_applicant")
        if not profile:
            profile = ApplicantProfile(
                id=req.profile_id or "prof_test",
                owner_id="usr_test",
                display_label="Simulation Applicant",
            )

        return PolicySimulator.simulate(
            req=req,
            strategy=strategy,
            profile=profile,
            is_emergency_stop_active=self.is_emergency_stop_active(),
        )

    def get_decisions_log(self, limit: int = 50) -> list[RecruitmentDecision]:
        return list(self._decisions_log.values())[-limit:]

    def get_decision(self, decision_id: str) -> Optional[RecruitmentDecision]:
        return self._decisions_log.get(decision_id)


# Global singleton instance
recruitment_policy_service = RecruitmentPolicyService()
