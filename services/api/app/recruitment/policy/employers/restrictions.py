"""Employer Restrictions, Allowlist/Blocklist Controller, and Identity Matcher (Stage 25)."""

from __future__ import annotations

import re
from typing import Optional
from app.recruitment.policy.contracts import (
    AllowlistMode,
    BlockedEmployerItem,
    EmployerRestrictions,
)


class EmployerRestrictionController:
    """Evaluates job employer identity against allowlists, blocklists, and organizational aliases."""

    @classmethod
    def normalize_company_name(cls, name: str) -> str:
        """Normalizes company name for cautious matching (lowercase, removes common legal suffixes)."""
        cleaned = name.lower().strip()
        # Remove common corporate designations for normalized comparison
        cleaned = re.sub(r"\b(inc|corp|corporation|llc|ltd|limited|co|company|group|technologies|solutions)\b\.?", "", cleaned)
        cleaned = re.sub(r"[^\w\s]", "", cleaned)
        return " ".join(cleaned.split())

    @classmethod
    def is_employer_blocked(
        cls,
        restrictions: EmployerRestrictions,
        employer_name: str,
        employer_domain: Optional[str] = None,
    ) -> tuple[bool, Optional[str]]:
        """Checks if employer matches an explicit entry on the blocklist.

        Returns:
            (is_blocked, reason)
        """
        norm_emp = cls.normalize_company_name(employer_name)
        norm_dom = employer_domain.lower().strip() if employer_domain else None

        for item in restrictions.blocked_employers:
            norm_blocked = cls.normalize_company_name(item.employer_name)

            # Exact normalized name match
            if norm_emp == norm_blocked:
                return True, item.reason or f"Explicit blocklist match for '{item.employer_name}'"

            # Domain match if domain supplied
            if norm_dom and item.domain:
                if norm_dom == item.domain.lower().strip() or norm_dom.endswith("." + item.domain.lower().strip()):
                    return True, item.reason or f"Employer domain '{norm_dom}' matches blocked domain '{item.domain}'"

        return False, None

    @classmethod
    def evaluate_allowlist(
        cls,
        restrictions: EmployerRestrictions,
        employer_name: str,
    ) -> tuple[bool, str]:
        """Evaluates whether the employer satisfies the allowlist policy.

        Returns:
            (is_permitted, explanation)
        """
        if restrictions.allowlist_mode == AllowlistMode.NO_ALLOWLIST:
            return True, "No allowlist active; employer accepted."

        norm_emp = cls.normalize_company_name(employer_name)
        matched = False
        for allowed in restrictions.allowed_employers:
            if norm_emp == cls.normalize_company_name(allowed):
                matched = True
                break

        if restrictions.allowlist_mode == AllowlistMode.STRICT_ALLOWLIST:
            if not matched:
                return False, f"Employer '{employer_name}' is not on the strict allowlist."
            return True, f"Employer '{employer_name}' is explicitly on the strict allowlist."

        # PREFER_ALLOWLIST mode
        if matched:
            return True, f"Employer '{employer_name}' is on the preferred allowlist."
        return True, f"Employer '{employer_name}' is not on the preferred allowlist, but allowed."

    @classmethod
    def is_identity_ambiguous(
        cls,
        employer_name: str,
        blocked_items: list[BlockedEmployerItem],
    ) -> tuple[bool, Optional[str]]:
        """Detects whether an employer name is dangerously similar to a blocked employer,
        requiring cautious human review rather than silent auto-decision.
        """
        norm_emp = cls.normalize_company_name(employer_name)
        words_emp = {w for w in norm_emp.split() if len(w) >= 4}

        for item in blocked_items:
            norm_b = cls.normalize_company_name(item.employer_name)
            if norm_emp == norm_b:
                continue

            # Substring check
            if norm_b in norm_emp or norm_emp in norm_b:
                return True, f"Employer '{employer_name}' has partial identity overlap with blocked entity '{item.employer_name}'"

            # Shared brand token check (e.g. "stripe" in "stripe payments" and "stripe global")
            words_b = {w for w in norm_b.split() if len(w) >= 4}
            common = words_emp.intersection(words_b)
            if common:
                return True, f"Employer '{employer_name}' has partial identity overlap with blocked entity '{item.employer_name}' (shared: {', '.join(common)})"

        return False, None
