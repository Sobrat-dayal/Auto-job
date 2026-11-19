"""Employer blocklist and restriction enforcement for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from app.recruitment.matching.contracts import CareerStrategySnapshotData

logger = logging.getLogger("autonom.recruitment.matching.conditions.employer_restrictions")


def evaluate_employer_restrictions(
    company_name: str,
    career_strategy: CareerStrategySnapshotData,
) -> tuple[bool, str | None]:
    """Enforces Stage 25 employer blocklists and restrictions (Section 60, Required Test 143).
    
    Returns (is_blocked, block_reason).
    """
    if not company_name:
        return False, None

    norm_company = company_name.strip().lower()

    # Required Test 143: Check explicit employer blocklist
    for blocked in career_strategy.blocked_employers:
        b_clean = blocked.strip().lower()
        if b_clean and (b_clean == norm_company or b_clean in norm_company or norm_company in b_clean):
            reason = f"Employer '{company_name}' is explicitly blocked by active career policy."
            logger.info(f"Hard policy violation: {reason}")
            return True, reason

    # Check strict allowlist if defined
    if career_strategy.preferred_employers:
        # If preferred employers are specified, they provide a soft bonus, not necessarily an exclusive allowlist
        pass

    return False, None
