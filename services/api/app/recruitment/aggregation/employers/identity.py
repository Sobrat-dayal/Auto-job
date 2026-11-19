"""Multi-Signal Employer Identity Resolution Engine (Stage 27)."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import CanonicalEmployerModel, EmployerIdentityDecisionModel
from app.recruitment.aggregation.contracts import (
    EmployerIdentityEvidence,
    EmployerIdentityStatus,
    OrganizationType,
)
from app.recruitment.aggregation.employers.aliases import (
    are_employer_names_equivalent,
    normalize_employer_name,
)
from app.recruitment.aggregation.employers.boards import extract_ats_board_token
from app.recruitment.aggregation.employers.domains import (
    extract_domain_from_url,
    is_corporate_domain,
)
from app.recruitment.aggregation.employers.registry import EmployerRegistry, employer_registry
from app.recruitment.aggregation.employers.relationships import classify_organization_type


class EmployerIdentityResolver:
    """Resolves arbitrary employer mentions to canonical employers using multi-signal evidence."""

    def __init__(self, registry: Optional[EmployerRegistry] = None) -> None:
        self.registry = registry or employer_registry

    async def resolve_employer(
        self,
        session: AsyncSession,
        raw_name: str,
        source_url: Optional[str] = None,
        provider: Optional[str] = None,
        description: Optional[str] = None,
    ) -> tuple[CanonicalEmployerModel, list[EmployerIdentityEvidence]]:
        """Resolve raw employer info to a CanonicalEmployer with evidence provenance."""
        evidence: list[EmployerIdentityEvidence] = []
        name_clean = raw_name.strip()

        # Only treat source_url domain as corporate domain if provider is an employer careers site
        is_direct_careers_site = provider in {"career_page", "employer_career_site"} or (
            source_url and not any(ats in source_url.lower() for ats in ["greenhouse.io", "lever.co", "ashbyhq.com"])
            and provider not in {"json_feed", "rss_atom", "manual_import"}
        )

        domain = extract_domain_from_url(source_url) if (source_url and is_direct_careers_site) else ""
        board_info = extract_ats_board_token(source_url, provider) if source_url else None

        # 1. Check verified corporate domain if present
        if domain and is_corporate_domain(domain):
            match_by_domain = await self.registry.find_by_domain(session, domain)
            if match_by_domain:
                evidence.append(
                    EmployerIdentityEvidence(
                        evidence_type="corporate_domain_match",
                        source_reference=domain,
                        observed_value=match_by_domain.name,
                        verification_status="verified",
                        confidence_delta=0.45,
                    )
                )
                return match_by_domain, evidence

        # 2. Check ATS provider board if present
        if board_info:
            b_prov, b_token = board_info
            match_by_board = await self.registry.find_by_board(session, b_prov, b_token)
            if match_by_board:
                evidence.append(
                    EmployerIdentityEvidence(
                        evidence_type="ats_board_match",
                        source_reference=f"{b_prov}:{b_token}",
                        observed_value=match_by_board.name,
                        verification_status="verified",
                        confidence_delta=0.40,
                    )
                )
                return match_by_board, evidence

        # 3. Check alias registry
        match_by_alias = await self.registry.find_by_alias(session, name_clean)
        if match_by_alias:
            evidence.append(
                EmployerIdentityEvidence(
                    evidence_type="alias_registry_match",
                    source_reference=name_clean,
                    observed_value=match_by_alias.name,
                    verification_status="strongly_supported",
                    confidence_delta=0.35,
                )
            )
            return match_by_alias, evidence

        # 4. Check normalized name match
        match_by_name = await self.registry.find_by_normalized_name(session, name_clean)
        if match_by_name:
            # Check domain contradiction before accepting if both have verified corporate domains
            if domain and match_by_name.primary_domain and is_corporate_domain(domain):
                if domain != match_by_name.primary_domain:
                    # Domain conflict! (e.g. Alpha Technologies vs Alpha Consulting)
                    pass
                else:
                    evidence.append(
                        EmployerIdentityEvidence(
                            evidence_type="normalized_name_match",
                            source_reference=name_clean,
                            observed_value=match_by_name.name,
                            verification_status="probable",
                            confidence_delta=0.30,
                        )
                    )
                    return match_by_name, evidence
            else:
                evidence.append(
                    EmployerIdentityEvidence(
                        evidence_type="normalized_name_match",
                        source_reference=name_clean,
                        observed_value=match_by_name.name,
                        verification_status="probable",
                        confidence_delta=0.30,
                    )
                )
                return match_by_name, evidence

        # 5. No match -> Create new Canonical Employer
        org_type = classify_organization_type(name_clean, description)
        corp_domain = domain if (domain and is_corporate_domain(domain)) else None

        new_emp = await self.registry.create_employer(
            session=session,
            name=name_clean,
            organization_type=org_type,
            identity_status=EmployerIdentityStatus.PROBABLE,
            official_careers_url=source_url if corp_domain else None,
            primary_domain=corp_domain,
            confidence_score=0.85 if corp_domain else 0.70,
        )

        evidence.append(
            EmployerIdentityEvidence(
                evidence_type="new_employer_registered",
                source_reference=name_clean,
                observed_value=new_emp.name,
                verification_status="probable",
                confidence_delta=0.0,
            )
        )

        return new_emp, evidence


employer_identity_resolver = EmployerIdentityResolver()
