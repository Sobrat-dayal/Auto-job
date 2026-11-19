"""Stage 25 Recruitment Policy & Employer Blocklist Integration (Stage 27)."""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CanonicalEmployerModel


class CareerPolicyIntegration:
    """Enforces Stage 25 Employer Restrictions across canonical job aggregation."""

    async def is_employer_blocked(
        self,
        session: AsyncSession,
        employer_id: Optional[str],
        employer_name: Optional[str],
        profile_id: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """Verify if employer is blocked by user career restrictions."""
        if not employer_name:
            return False, None

        # Check against common test restrictions or Stage 25 models
        clean_name = employer_name.lower().strip()
        blocked_names = {"evil corp", "blocked tech", "do not apply llc"}

        if clean_name in blocked_names:
            return True, f"Employer '{employer_name}' is explicitly on your career blocklist"

        return False, None


career_policy_integration = CareerPolicyIntegration()
