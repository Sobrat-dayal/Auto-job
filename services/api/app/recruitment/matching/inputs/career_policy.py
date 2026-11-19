"""Career Policy resolver for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from app.recruitment.matching.contracts import CareerStrategySnapshotData
from app.recruitment.matching.errors import CareerStrategyNotFoundError
from app.recruitment.policy.service import recruitment_policy_service as career_policy_service

logger = logging.getLogger("autonom.recruitment.matching.inputs.career_policy")


def resolve_career_policy(strategy_id: str | None = None) -> CareerStrategySnapshotData:
    """Loads authoritative recruitment preferences and restrictions from Stage 25."""
    try:
        if strategy_id:
            strat = career_policy_service.get_strategy(strategy_id)
        else:
            strat = career_policy_service.get_active_strategy()
    except Exception as exc:
        logger.warning(f"Error fetching strategy '{strategy_id}': {exc}")
        strat = None

    if not strat:
        # Default permissive fallback strategy if none exists
        return CareerStrategySnapshotData(
            strategy_id="strat_default",
            title="Default Career Strategy",
            is_active=True,
            role_families=["Software Engineering", "Backend", "Full-Stack", "Machine Learning"],
            target_locations=[],
            excluded_locations=[],
            work_arrangements=["remote", "hybrid", "on_site"],
            relocation_preference="not_willing",
            min_annual_salary=None,
            target_annual_salary=None,
            salary_currency="USD",
            undisclosed_salary_handling="review",
            blocked_employers=[],
            preferred_employers=[],
            allowed_employment_types=["full_time", "internship", "contract"],
        )

    # Extract target and excluded locations
    target_locs: list[str] = []
    excluded_locs: list[str] = []
    if strat.geographic_preferences:
        target_locs = list(strat.geographic_preferences.preferred_countries) + list(strat.geographic_preferences.preferred_cities)
        excluded_locs = list(strat.geographic_preferences.excluded_countries) + list(strat.geographic_preferences.excluded_cities)

    # Extract role families
    role_fams = [rf.value if hasattr(rf, "value") else str(rf) for rf in strat.role_families]

    # Extract employment types
    emp_types = [et.value if hasattr(et, "value") else str(et) for et in strat.allowed_employment_types]

    # Extract work arrangements
    arrangements = [wa.value if hasattr(wa, "value") else str(wa) for wa in strat.work_arrangements]

    # Extract compensation policy
    comp = strat.compensation_policy
    min_sal = comp.absolute_minimum if comp else None
    target_sal = comp.target_salary if comp else None
    curr = comp.currency if comp else "USD"
    undisclosed = comp.undisclosed_handling.value if comp and hasattr(comp.undisclosed_handling, "value") else "review"

    # Extract employer blocklist
    blocked: list[str] = []
    if strat.employer_restrictions and strat.employer_restrictions.blocked_employers:
        blocked = [b.name.lower().strip() for b in strat.employer_restrictions.blocked_employers]

    return CareerStrategySnapshotData(
        strategy_id=strat.id,
        title=strat.title,
        is_active=strat.is_active,
        role_families=role_fams,
        target_locations=target_locs,
        excluded_locations=excluded_locs,
        work_arrangements=arrangements,
        relocation_preference=strat.relocation_preference.value if hasattr(strat.relocation_preference, "value") else "not_willing",
        min_annual_salary=min_sal,
        target_annual_salary=target_sal,
        salary_currency=curr,
        undisclosed_salary_handling=undisclosed,
        blocked_employers=blocked,
        preferred_employers=[],
        allowed_employment_types=emp_types,
    )
