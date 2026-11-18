"""Deterministic Rules, Precedence Evaluator, and Policy Conflict Detector (Stage 25)."""

from __future__ import annotations

from typing import Optional
from app.recruitment.policy.compensation.normalizer import CompensationNormalizer
from app.recruitment.policy.contracts import (
    AllowlistMode,
    CareerStrategy,
    CompensationMatchStatus,
    ConflictSeverity,
    HardConstraintEvaluation,
    JobEligibilityAssessment,
    JobOpportunityContext,
    PolicyConflictItem,
    PolicyDecisionOutcome,
    RecruitmentDecision,
    ReviewTrigger,
    SoftPreferenceEvaluation,
    WorkArrangement,
)
from app.recruitment.policy.employers.restrictions import EmployerRestrictionController
from app.recruitment.policy.taxonomy.roles import RoleTaxonomyEngine


class PolicyRulesEngine:
    """Evaluates hard constraints, computes soft preferences, and determines overall decision based on precedence."""

    @classmethod
    def evaluate_decision(
        cls,
        strategy: CareerStrategy,
        job: JobOpportunityContext,
        eligibility: JobEligibilityAssessment,
        is_emergency_stop_active: bool = False,
        is_source_blocked: bool = False,
    ) -> RecruitmentDecision:
        hard_constraints: list[HardConstraintEvaluation] = []
        soft_preferences: list[SoftPreferenceEvaluation] = []
        review_triggers: list[ReviewTrigger] = list(eligibility.review_triggers)

        # Precedence Level 1: Emergency Stop
        if is_emergency_stop_active:
            return cls._make_decision(
                job=job,
                strategy=strategy,
                outcome=PolicyDecisionOutcome.PROHIBITED_BY_POLICY,
                precedence="Level 1: Emergency Stop active",
                explanation="Operation prohibited: Global Emergency Stop is engaged across all recruitment actions.",
                eligibility=eligibility,
                hard_constraints=[
                    HardConstraintEvaluation(
                        rule_id="rule_emerg_stop",
                        rule_name="Global Emergency Stop",
                        passed=False,
                        reason="Emergency Stop is currently active",
                    )
                ],
                soft_preferences=[],
                review_triggers=review_triggers,
                denied_actions=["discover", "prepare_resume", "prepare_answers", "submit"],
            )

        # Precedence Level 4: Platform and Source Restrictions
        if is_source_blocked or job.source_platform in strategy.sources.blocked_sources:
            return cls._make_decision(
                job=job,
                strategy=strategy,
                outcome=PolicyDecisionOutcome.PROHIBITED_BY_POLICY,
                precedence="Level 4: Source platform restriction",
                explanation=f"Source platform '{job.source_platform}' is explicitly blocked by candidate policy.",
                eligibility=eligibility,
                hard_constraints=[
                    HardConstraintEvaluation(
                        rule_id="rule_source_blocked",
                        rule_name="Blocked Source Platform",
                        passed=False,
                        reason=f"Platform '{job.source_platform}' is blocked",
                    )
                ],
                soft_preferences=[],
                review_triggers=review_triggers,
                denied_actions=["prepare_resume", "prepare_answers", "submit"],
            )

        # Precedence Level 6: Explicit Employer Blocklist
        is_blocked, block_reason = EmployerRestrictionController.is_employer_blocked(
            restrictions=strategy.employers,
            employer_name=job.employer_name,
            employer_domain=job.employer_domain,
        )
        if is_blocked:
            return cls._make_decision(
                job=job,
                strategy=strategy,
                outcome=PolicyDecisionOutcome.PROHIBITED_BY_POLICY,
                precedence="Level 6: Employer blocklist enforcement",
                explanation=f"Employer '{job.employer_name}' is on candidate blocklist: {block_reason}.",
                eligibility=eligibility,
                hard_constraints=[
                    HardConstraintEvaluation(
                        rule_id="rule_employer_blocklist",
                        rule_name="Employer Blocklist",
                        passed=False,
                        reason=block_reason or f"Employer '{job.employer_name}' is blocked",
                    )
                ],
                soft_preferences=[],
                review_triggers=review_triggers,
                denied_actions=["prepare_resume", "prepare_answers", "submit"],
            )

        # Check Strict Allowlist
        allowlist_ok, allowlist_exp = EmployerRestrictionController.evaluate_allowlist(
            restrictions=strategy.employers,
            employer_name=job.employer_name,
        )
        if not allowlist_ok:
            return cls._make_decision(
                job=job,
                strategy=strategy,
                outcome=PolicyDecisionOutcome.PROHIBITED_BY_POLICY,
                precedence="Level 6: Strict allowlist enforcement",
                explanation=allowlist_exp,
                eligibility=eligibility,
                hard_constraints=[
                    HardConstraintEvaluation(
                        rule_id="rule_strict_allowlist",
                        rule_name="Strict Employer Allowlist",
                        passed=False,
                        reason=allowlist_exp,
                    )
                ],
                soft_preferences=[],
                review_triggers=review_triggers,
                denied_actions=["prepare_resume", "prepare_answers", "submit"],
            )

        # Check Ambiguous Employer Identity
        is_ambiguous, amb_reason = EmployerRestrictionController.is_identity_ambiguous(
            job.employer_name, strategy.employers.blocked_employers
        )
        if is_ambiguous:
            review_triggers.append(ReviewTrigger.EMPLOYER_IDENTITY_UNCERTAIN)

        # Precedence Level 7: Hard Eligibility Disqualifications
        if eligibility.has_blocking_disqualification:
            failed_cats = [k for k, v in eligibility.categories.items() if v.outcome.value == "does_not_meet_requirement"]
            return cls._make_decision(
                job=job,
                strategy=strategy,
                outcome=PolicyDecisionOutcome.INELIGIBLE,
                precedence="Level 7: Hard eligibility requirement failure",
                explanation=f"Applicant does not satisfy mandatory requirements: {', '.join(failed_cats)}.",
                eligibility=eligibility,
                hard_constraints=[
                    HardConstraintEvaluation(
                        rule_id=f"rule_elig_{cat}",
                        rule_name=f"Mandatory Eligibility: {cat.capitalize()}",
                        passed=False,
                        reason=eligibility.categories[cat].explanation,
                    )
                    for cat in failed_cats
                ],
                soft_preferences=[],
                review_triggers=review_triggers,
                denied_actions=["prepare_resume", "prepare_answers", "submit"],
            )

        # Precedence Level 8: Hard Career Preferences
        # A. Excluded Job Titles
        for target in strategy.target_roles:
            if target.is_excluded and target.title.lower() in job.title.lower():
                return cls._make_decision(
                    job=job,
                    strategy=strategy,
                    outcome=PolicyDecisionOutcome.REJECTED_BY_PREFERENCE,
                    precedence="Level 8: Hard excluded job title",
                    explanation=f"Job title '{job.title}' contains explicitly excluded title '{target.title}'.",
                    eligibility=eligibility,
                    hard_constraints=[
                        HardConstraintEvaluation(
                            rule_id="rule_excluded_title",
                            rule_name="Excluded Job Title",
                            passed=False,
                            reason=f"Title '{target.title}' is on candidate exclusion list",
                        )
                    ],
                    soft_preferences=[],
                    review_triggers=review_triggers,
                    denied_actions=["prepare_resume", "prepare_answers", "submit"],
                )

        # B. Hard Work Arrangement (e.g. Remote Only)
        if strategy.work_arrangement.is_hard_constraint:
            if job.work_arrangement not in strategy.work_arrangement.allowed_arrangements:
                return cls._make_decision(
                    job=job,
                    strategy=strategy,
                    outcome=PolicyDecisionOutcome.REJECTED_BY_PREFERENCE,
                    precedence="Level 8: Hard work arrangement constraint",
                    explanation=f"Position work arrangement '{job.work_arrangement.value}' is not among allowed arrangements ({', '.join(a.value for a in strategy.work_arrangement.allowed_arrangements)}).",
                    eligibility=eligibility,
                    hard_constraints=[
                        HardConstraintEvaluation(
                            rule_id="rule_hard_work_arrangement",
                            rule_name="Hard Work Arrangement Constraint",
                            passed=False,
                            reason=f"Arrangement '{job.work_arrangement.value}' is disallowed",
                        )
                    ],
                    soft_preferences=[],
                    review_triggers=review_triggers,
                    denied_actions=["prepare_resume", "prepare_answers", "submit"],
                )

        # C. Hard Location Exclusions
        if job.location_city and any(exc.lower() in job.location_city.lower() for exc in strategy.geography.excluded_locations):
            return cls._make_decision(
                job=job,
                strategy=strategy,
                outcome=PolicyDecisionOutcome.REJECTED_BY_PREFERENCE,
                precedence="Level 8: Hard excluded location",
                explanation=f"Location '{job.location_city}' is explicitly on candidate location exclusion list.",
                eligibility=eligibility,
                hard_constraints=[
                    HardConstraintEvaluation(
                        rule_id="rule_excluded_location",
                        rule_name="Excluded Location",
                        passed=False,
                        reason=f"City '{job.location_city}' is excluded",
                    )
                ],
                soft_preferences=[],
                review_triggers=review_triggers,
                denied_actions=["prepare_resume", "prepare_answers", "submit"],
            )

        # D. Remote country restriction check
        if job.work_arrangement == WorkArrangement.REMOTE and job.remote_country_restriction:
            if strategy.geography.country.lower() != job.remote_country_restriction.lower():
                return cls._make_decision(
                    job=job,
                    strategy=strategy,
                    outcome=PolicyDecisionOutcome.REJECTED_BY_PREFERENCE,
                    precedence="Level 8: Remote country boundary restriction",
                    explanation=f"Remote role is restricted to residents of {job.remote_country_restriction}, but candidate country is {strategy.geography.country}.",
                    eligibility=eligibility,
                    hard_constraints=[
                        HardConstraintEvaluation(
                            rule_id="rule_remote_country",
                            rule_name="Remote Country Eligibility",
                            passed=False,
                            reason=f"Restricted to {job.remote_country_restriction}",
                        )
                    ],
                    soft_preferences=[],
                    review_triggers=review_triggers,
                    denied_actions=["prepare_resume", "prepare_answers", "submit"],
                )

        # E. Hard Compensation Minimum
        comp_status, annual_val, comp_exp = CompensationNormalizer.evaluate_compensation(
            policy=strategy.compensation,
            offered_min=job.compensation_min,
            offered_max=job.compensation_max,
            offered_currency=job.compensation_currency,
            offered_unit=job.compensation_unit,
        )
        if strategy.compensation.is_hard_minimum and comp_status == CompensationMatchStatus.BELOW_MINIMUM:
            return cls._make_decision(
                job=job,
                strategy=strategy,
                outcome=PolicyDecisionOutcome.REJECTED_BY_PREFERENCE,
                precedence="Level 8: Hard compensation threshold",
                explanation=comp_exp,
                eligibility=eligibility,
                hard_constraints=[
                    HardConstraintEvaluation(
                        rule_id="rule_hard_compensation_min",
                        rule_name="Minimum Acceptable Compensation",
                        passed=False,
                        reason=comp_exp,
                    )
                ],
                soft_preferences=[],
                review_triggers=review_triggers,
                denied_actions=["prepare_resume", "prepare_answers", "submit"],
            )

        if comp_status == CompensationMatchStatus.COMPENSATION_UNKNOWN:
            if strategy.compensation.undisclosed_handling.value == "exclude":
                return cls._make_decision(
                    job=job,
                    strategy=strategy,
                    outcome=PolicyDecisionOutcome.REJECTED_BY_PREFERENCE,
                    precedence="Level 8: Undisclosed compensation excluded",
                    explanation=comp_exp,
                    eligibility=eligibility,
                    hard_constraints=[],
                    soft_preferences=[],
                    review_triggers=review_triggers,
                    denied_actions=["prepare_resume", "prepare_answers", "submit"],
                )
            elif strategy.compensation.undisclosed_handling.value == "require_review":
                review_triggers.append(ReviewTrigger.COMPENSATION_UNDISCLOSED)

        # Compute Soft Preferences
        total_weight = 0.0
        weighted_score = 0.0

        # Role relevance soft score
        role_pref = cls._evaluate_role_soft_preference(strategy, job)
        soft_preferences.append(role_pref)
        weighted_score += role_pref.score * role_pref.weight
        total_weight += role_pref.weight

        # Work arrangement soft score
        arr_pref = cls._evaluate_arrangement_soft_preference(strategy, job)
        soft_preferences.append(arr_pref)
        weighted_score += arr_pref.score * arr_pref.weight
        total_weight += arr_pref.weight

        # Compensation soft score
        comp_pref = cls._evaluate_compensation_soft_preference(strategy, comp_status, comp_exp)
        soft_preferences.append(comp_pref)
        weighted_score += comp_pref.score * comp_pref.weight
        total_weight += comp_pref.weight

        # Overall soft score calculation
        overall_score = round(weighted_score / total_weight, 1) if total_weight > 0 else 75.0

        # Precedence Level 5 / 9 / 10 Decision
        if review_triggers:
            return cls._make_decision(
                job=job,
                strategy=strategy,
                outcome=PolicyDecisionOutcome.NEEDS_REVIEW,
                precedence="Level 5: Sensitive decision or uncertain eligibility triggers review",
                explanation=f"Position meets basic criteria with overall score {overall_score:.1f}, but requires human review for: {', '.join(t.value for t in review_triggers)}.",
                eligibility=eligibility,
                hard_constraints=[HardConstraintEvaluation(rule_id="all_hard", rule_name="Hard Constraints", passed=True, reason="All hard rules satisfied")],
                soft_preferences=soft_preferences,
                review_triggers=review_triggers,
                score=overall_score,
                permitted_actions=["analyze", "prepare_draft_materials"],
                denied_actions=["autonomous_submission"],
            )

        return cls._make_decision(
            job=job,
            strategy=strategy,
            outcome=PolicyDecisionOutcome.PROCEED,
            precedence="Level 10: Soft preference ranking passed",
            explanation=f"Position satisfies all eligibility criteria and career preferences (Score: {overall_score:.1f}/100).",
            eligibility=eligibility,
            hard_constraints=[HardConstraintEvaluation(rule_id="all_hard", rule_name="Hard Constraints", passed=True, reason="All hard rules satisfied")],
            soft_preferences=soft_preferences,
            review_triggers=[],
            score=overall_score,
            permitted_actions=["discover", "prepare_resume", "prepare_answers", "review_ready"],
            denied_actions=[],
        )

    @classmethod
    def _evaluate_role_soft_preference(cls, strategy: CareerStrategy, job: JobOpportunityContext) -> SoftPreferenceEvaluation:
        matched_roles = [
            t.title for t in strategy.target_roles
            if not t.is_excluded and (t.title.lower() in job.title.lower() or job.title.lower() in t.title.lower())
        ]
        if matched_roles:
            return SoftPreferenceEvaluation(
                preference_name="Target Role Title Match",
                weight=2.0,
                score=100.0,
                matched_elements=matched_roles,
                explanation=f"Job title aligns with target role preference(s): {', '.join(matched_roles)}.",
            )

        # Check role family match
        family = job.role_family or RoleTaxonomyEngine.classify_role_family(job.title)
        family_match = any(t.role_family == family for t in strategy.target_roles if not t.is_excluded)
        if family_match:
            return SoftPreferenceEvaluation(
                preference_name="Role Family Alignment",
                weight=1.5,
                score=75.0,
                matched_elements=[family.value],
                explanation=f"Job role family '{family.value}' aligns with candidate target categories.",
            )

        return SoftPreferenceEvaluation(
            preference_name="Role Relevance",
            weight=1.0,
            score=50.0,
            explanation=f"Job title '{job.title}' has general engineering relevance but lacks direct title match.",
        )

    @classmethod
    def _evaluate_arrangement_soft_preference(cls, strategy: CareerStrategy, job: JobOpportunityContext) -> SoftPreferenceEvaluation:
        if job.work_arrangement == strategy.work_arrangement.preferred_arrangement:
            return SoftPreferenceEvaluation(
                preference_name="Work Arrangement",
                weight=1.5,
                score=100.0,
                matched_elements=[job.work_arrangement.value],
                explanation=f"Matches preferred work arrangement '{job.work_arrangement.value}'.",
            )
        elif job.work_arrangement in strategy.work_arrangement.allowed_arrangements:
            return SoftPreferenceEvaluation(
                preference_name="Work Arrangement",
                weight=1.0,
                score=70.0,
                matched_elements=[job.work_arrangement.value],
                explanation=f"Arrangement '{job.work_arrangement.value}' is acceptable though not primary preference.",
            )
        return SoftPreferenceEvaluation(
            preference_name="Work Arrangement",
            weight=1.0,
            score=30.0,
            explanation=f"Arrangement '{job.work_arrangement.value}' is outside typical preferences.",
        )

    @classmethod
    def _evaluate_compensation_soft_preference(
        cls,
        strategy: CareerStrategy,
        status: CompensationMatchStatus,
        explanation: str,
    ) -> SoftPreferenceEvaluation:
        score_map = {
            CompensationMatchStatus.WITHIN_PREFERRED_RANGE: 100.0,
            CompensationMatchStatus.ABOVE_PREFERRED_RANGE: 100.0,
            CompensationMatchStatus.MEETS_MINIMUM: 75.0,
            CompensationMatchStatus.COMPENSATION_UNKNOWN: 60.0,
            CompensationMatchStatus.BELOW_MINIMUM: 20.0,
            CompensationMatchStatus.NOT_COMPARABLE: 50.0,
        }
        return SoftPreferenceEvaluation(
            preference_name="Compensation Competitiveness",
            weight=1.5,
            score=score_map.get(status, 50.0),
            explanation=explanation,
        )

    @classmethod
    def _make_decision(
        cls,
        job: JobOpportunityContext,
        strategy: CareerStrategy,
        outcome: PolicyDecisionOutcome,
        precedence: str,
        explanation: str,
        eligibility: JobEligibilityAssessment,
        hard_constraints: list[HardConstraintEvaluation],
        soft_preferences: list[SoftPreferenceEvaluation],
        review_triggers: list[ReviewTrigger],
        score: float = 0.0,
        permitted_actions: Optional[list[str]] = None,
        denied_actions: Optional[list[str]] = None,
    ) -> RecruitmentDecision:
        return RecruitmentDecision(
            job_id=job.id,
            job_title=job.title,
            employer=job.employer_name,
            strategy_id=strategy.id,
            policy_version=1,
            decision=outcome,
            overall_score=score,
            eligibility_assessment=eligibility,
            hard_constraints=hard_constraints,
            soft_preferences=soft_preferences,
            precedence_rule_applied=precedence,
            review_triggers=review_triggers,
            permitted_future_actions=permitted_actions or [],
            denied_future_actions=denied_actions or [],
            explanation=explanation,
        )

    @classmethod
    def detect_conflicts(cls, strategy: CareerStrategy) -> list[PolicyConflictItem]:
        """Scans a career strategy for mutually contradictory configuration rules."""
        conflicts: list[PolicyConflictItem] = []

        # 1. Remote Only + On-site Conflict
        if strategy.work_arrangement.is_hard_constraint:
            if WorkArrangement.REMOTE in strategy.work_arrangement.allowed_arrangements and len(strategy.work_arrangement.allowed_arrangements) == 1:
                # If only remote is allowed, check if any city requires onsite
                if strategy.geography.allowed_cities:
                    conflicts.append(
                        PolicyConflictItem(
                            title="Remote-Only vs Allowed Cities Conflict",
                            description="Work arrangement is strictly locked to 'Remote Only', but specific mandatory on-site cities are configured.",
                            rules_involved=["work_arrangement.allowed_arrangements", "geography.allowed_cities"],
                            severity=ConflictSeverity.WARNING,
                            suggested_resolution="Allow Hybrid arrangement or remove specific city constraints.",
                        )
                    )

        # 2. Compensation Min > Preferred Max
        if strategy.compensation.preferred_max and strategy.compensation.min_acceptable_amount > strategy.compensation.preferred_max:
            conflicts.append(
                PolicyConflictItem(
                    title="Minimum Acceptable Salary Exceeds Preferred Max",
                    description=f"Minimum acceptable salary ({strategy.compensation.min_acceptable_amount}) is greater than preferred maximum ({strategy.compensation.preferred_max}).",
                    rules_involved=["compensation.min_acceptable_amount", "compensation.preferred_max"],
                    severity=ConflictSeverity.BLOCKING,
                    suggested_resolution="Increase preferred maximum or lower minimum acceptable threshold.",
                )
            )

        # 3. Allowlist vs Blocklist Overlap
        blocked_names = {EmployerRestrictionController.normalize_company_name(b.employer_name) for b in strategy.employers.blocked_employers}
        for allowed in strategy.employers.allowed_employers:
            norm_a = EmployerRestrictionController.normalize_company_name(allowed)
            if norm_a in blocked_names:
                conflicts.append(
                    PolicyConflictItem(
                        title=f"Employer '{allowed}' in Both Allowlist and Blocklist",
                        description=f"Employer '{allowed}' is present on both the allowlist and the blocklist. Blocklist takes absolute precedence.",
                        rules_involved=["employers.allowed_employers", "employers.blocked_employers"],
                        severity=ConflictSeverity.ERROR,
                        suggested_resolution="Remove the employer from either the allowlist or the blocklist.",
                    )
                )

        return conflicts
