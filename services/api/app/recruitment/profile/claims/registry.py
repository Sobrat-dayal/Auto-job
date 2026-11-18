"""Canonical Applicant Claim Registry, Provenance Tracker, and Conflict Resolution Engine."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Optional
from uuid import uuid4

from app.recruitment.profile.contracts import (
    ApplicantClaim,
    ApplicantProfile,
    ClaimCategory,
    ProfileConflict,
    VerificationStatus,
)
from app.recruitment.profile.errors import ClaimNotFoundError, ConflictResolutionError

logger = logging.getLogger("autonom.recruitment.profile.claims")


class ClaimRegistry:
    """Manages the lifecycle of atomic applicant claims, provenance records, and conflicts."""

    def __init__(self) -> None:
        self._claims: dict[str, ApplicantClaim] = {}
        self._conflicts: dict[str, ProfileConflict] = {}

    def register_claim(self, claim: ApplicantClaim) -> ApplicantClaim:
        self._claims[claim.claim_id] = claim
        return claim

    def get_claim(self, claim_id: str) -> Optional[ApplicantClaim]:
        return self._claims.get(claim_id)

    def list_claims(
        self,
        profile_id: str,
        category: Optional[ClaimCategory] = None,
        status: Optional[VerificationStatus] = None,
    ) -> list[ApplicantClaim]:
        results = [c for c in self._claims.values() if c.profile_id == profile_id]
        if category:
            results = [c for c in results if c.category == category]
        if status:
            results = [c for c in results if c.verification_status == status]
        return sorted(results, key=lambda c: c.created_at, reverse=True)

    def confirm_claim(self, claim_id: str) -> ApplicantClaim:
        claim = self._claims.get(claim_id)
        if not claim:
            raise ClaimNotFoundError(f"Claim '{claim_id}' not found.")
        claim.verification_status = VerificationStatus.USER_CONFIRMED
        claim.updated_at = datetime.now(UTC)
        return claim

    def reject_claim(self, claim_id: str) -> ApplicantClaim:
        claim = self._claims.get(claim_id)
        if not claim:
            raise ClaimNotFoundError(f"Claim '{claim_id}' not found.")
        claim.verification_status = VerificationStatus.REJECTED
        claim.updated_at = datetime.now(UTC)
        return claim

    def supersede_claim(self, old_claim_id: str, new_claim: ApplicantClaim) -> tuple[ApplicantClaim, ApplicantClaim]:
        old_claim = self._claims.get(old_claim_id)
        if not old_claim:
            raise ClaimNotFoundError(f"Old claim '{old_claim_id}' not found.")
        old_claim.verification_status = VerificationStatus.SUPERSEDED
        old_claim.updated_at = datetime.now(UTC)

        new_claim.supersedes_claim_id = old_claim_id
        new_claim.version = old_claim.version + 1
        self._claims[new_claim.claim_id] = new_claim
        return old_claim, new_claim

    def detect_conflicts(self, profile_id: str) -> list[ProfileConflict]:
        """Detects contradictions among active claims in the profile."""
        active_claims = [
            c
            for c in self._claims.values()
            if c.profile_id == profile_id
            and c.verification_status not in (VerificationStatus.SUPERSEDED, VerificationStatus.REJECTED)
        ]

        conflicts: list[ProfileConflict] = []
        # Group by category and normalized entity
        edu_claims = [c for c in active_claims if c.category == ClaimCategory.DEGREE]
        for i in range(len(edu_claims)):
            for j in range(i + 1, len(edu_claims)):
                ca, cb = edu_claims[i], edu_claims[j]
                if ca.normalized_value != cb.normalized_value:
                    # Check if they claim same degree from same institution with different dates
                    if ca.source_ref == cb.source_ref:
                        c_id = f"cfl_{uuid4().hex[:8]}"
                        conf = ProfileConflict(
                            conflict_id=c_id,
                            profile_id=profile_id,
                            claim_id_a=ca.claim_id,
                            claim_id_b=cb.claim_id,
                            category=ClaimCategory.DEGREE,
                            field_name="education.degree",
                            description=f"Conflicting degree claims: '{ca.normalized_value}' vs '{cb.normalized_value}'",
                        )
                        self._conflicts[c_id] = conf
                        conflicts.append(conf)

        return conflicts

    def resolve_conflict(self, conflict_id: str, accepted_claim_id: str) -> ProfileConflict:
        conflict = self._conflicts.get(conflict_id)
        if not conflict:
            raise ConflictResolutionError(f"Conflict '{conflict_id}' not found.")
        if accepted_claim_id not in (conflict.claim_id_a, conflict.claim_id_b):
            raise ConflictResolutionError(f"Claim '{accepted_claim_id}' is not part of conflict '{conflict_id}'.")

        rejected_claim_id = (
            conflict.claim_id_b if accepted_claim_id == conflict.claim_id_a else conflict.claim_id_a
        )
        self.confirm_claim(accepted_claim_id)
        self.reject_claim(rejected_claim_id)

        conflict.resolution_status = "resolved"
        conflict.resolved_claim_id = accepted_claim_id
        conflict.resolved_at = datetime.now(UTC)
        return conflict

    def list_conflicts(self, profile_id: str) -> list[ProfileConflict]:
        return [c for c in self._conflicts.values() if c.profile_id == profile_id and c.resolution_status == "pending"]

    def sync_from_profile(self, profile: ApplicantProfile) -> list[ApplicantClaim]:
        """Synchronizes atomic claim entities from the canonical profile entities."""
        existing_claims = {c.normalized_value: c for c in self._claims.values() if c.profile_id == profile.id}
        created_or_updated: list[ApplicantClaim] = []

        # Education claims
        for edu in profile.education:
            val = f"Degree: {edu.degree} in {edu.field_of_study} from {edu.institution} ({edu.start_date or '?'}-{edu.end_date or '?'})"
            if val not in existing_claims:
                claim = ApplicantClaim(
                    profile_id=profile.id,
                    category=ClaimCategory.DEGREE,
                    normalized_value=val,
                    original_text=f"{edu.degree}, {edu.field_of_study} at {edu.institution}",
                    evidence_refs=edu.evidence_refs,
                    source_category="profile_entity",
                    verification_status=edu.verification_status,
                )
                self.register_claim(claim)
                created_or_updated.append(claim)

        # Experience claims
        for exp in profile.experience:
            val = f"Employment: {exp.job_title} at {exp.employer} ({exp.start_date}-{exp.end_date or 'Present'})"
            if val not in existing_claims:
                claim = ApplicantClaim(
                    profile_id=profile.id,
                    category=ClaimCategory.EMPLOYMENT,
                    normalized_value=val,
                    original_text=f"{exp.job_title} at {exp.employer}",
                    evidence_refs=exp.evidence_refs,
                    source_category="profile_entity",
                    verification_status=exp.verification_status,
                )
                self.register_claim(claim)
                created_or_updated.append(claim)

            # Achievement claims
            for ach in exp.achievements:
                ach_val = f"Achievement at {exp.employer}: {ach.statement}"
                if ach_val not in existing_claims:
                    ach_claim = ApplicantClaim(
                        profile_id=profile.id,
                        category=ClaimCategory.ACHIEVEMENT,
                        normalized_value=ach_val,
                        original_text=ach.statement,
                        evidence_refs=exp.evidence_refs,
                        source_category="profile_entity",
                        verification_status=ach.verification_status,
                    )
                    self.register_claim(ach_claim)
                    created_or_updated.append(ach_claim)

        # Skill claims
        for skl in profile.skills:
            val = f"Skill: {skl.name} ({skl.category.value})"
            if val not in existing_claims:
                claim = ApplicantClaim(
                    profile_id=profile.id,
                    category=ClaimCategory.SKILL,
                    normalized_value=val,
                    original_text=skl.name,
                    evidence_refs=skl.evidence_refs,
                    source_category="profile_entity",
                    verification_status=skl.verification_status,
                )
                self.register_claim(claim)
                created_or_updated.append(claim)

        # Project claims
        for prj in profile.projects:
            val = f"Project: {prj.title}"
            if val not in existing_claims:
                claim = ApplicantClaim(
                    profile_id=profile.id,
                    category=ClaimCategory.CONTRIBUTION,
                    normalized_value=val,
                    original_text=f"{prj.title}: {prj.applicant_contribution or prj.description}",
                    evidence_refs=prj.evidence_refs,
                    source_category="profile_entity",
                    verification_status=prj.verification_status,
                )
                self.register_claim(claim)
                created_or_updated.append(claim)

        # Certification claims
        for crt in profile.certifications:
            val = f"Certification: {crt.title} issued by {crt.issuing_org}"
            if val not in existing_claims:
                claim = ApplicantClaim(
                    profile_id=profile.id,
                    category=ClaimCategory.CERTIFICATION,
                    normalized_value=val,
                    original_text=f"{crt.title} ({crt.issuing_org})",
                    evidence_refs=[crt.evidence_ref] if crt.evidence_ref else [],
                    source_category="profile_entity",
                    verification_status=crt.verification_status,
                )
                self.register_claim(claim)
                created_or_updated.append(claim)

        return created_or_updated

