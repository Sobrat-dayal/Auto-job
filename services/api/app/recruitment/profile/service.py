"""Authoritative Applicant Profile Service facade for AUTONOM (Stage 21)."""

from __future__ import annotations

import base64
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Optional
from uuid import uuid4

from app.core.config import settings
from app.core.security import AuthContext
from app.recruitment.profile.claims.registry import ClaimRegistry
from app.recruitment.profile.contracts import (
    AcademicStatus,
    AchievementItem,
    ApplicantClaim,
    ApplicantProfile,
    AwardRecord,
    CandidateReviewActionRequest,
    CandidateStatus,
    CertificationRecord,
    ClaimCategory,
    ContactInfo,
    DataQualityReport,
    EducationRecord,
    EmploymentEligibility,
    EmploymentRecord,
    EvidenceMetadata,
    ExtractionCandidate,
    ImportJob,
    ImportStatus,
    LocationInfo,
    ProfessionalLink,
    ProfileConflict,
    ProfileCreateRequest,
    ProfileSnapshot,
    ProfileUpdateRequest,
    ProfileVersionRecord,
    ProjectRecord,
    SkillCategory,
    SkillItem,
    VerificationStatus,
)
from app.recruitment.profile.errors import (
    ClaimNotFoundError,
    EvidenceNotFoundError,
    ImportJobNotFoundError,
    ProfileNotFoundError,
    ProfilePermissionDeniedError,
)
from app.recruitment.profile.import_pipeline.extractor import CandidateExtractor
from app.recruitment.profile.import_pipeline.parser import DocumentParser
from app.recruitment.profile.integrations.agents import AgentProfileAdapter
from app.recruitment.profile.integrations.authorization import (
    ProfileAuthorizationEnforcer,
    SCOPE_PROFILE_READ,
    SCOPE_PROFILE_UPDATE,
    SCOPE_PROFILE_DELETE,
    SCOPE_PROFILE_EXPORT,
)
from app.recruitment.profile.integrations.memory import ProfileMemorySync
from app.recruitment.profile.quality.checks import DataQualityEngine

logger = logging.getLogger("autonom.recruitment.profile.service")


class ApplicantProfileService:
    """The central single source of truth for all applicant identity, education, skills, and evidence."""

    def __init__(self) -> None:
        self._profiles: dict[str, ApplicantProfile] = {}
        self._evidence: dict[str, EvidenceMetadata] = {}
        self._imports: dict[str, ImportJob] = {}
        self._versions: dict[str, list[ProfileVersionRecord]] = {}
        self._claim_registry = ClaimRegistry()
        self._evidence_dir = settings.artifacts_dir / "evidence"
        self._evidence_dir.mkdir(parents=True, exist_ok=True)
        self._init_default_profile()

    def _init_default_profile(self) -> None:
        """Initializes a primary default profile container for local desktop owner."""
        default_id = "prof_primary_applicant"
        prof = ApplicantProfile(
            id=default_id,
            owner_id="default_user",
            display_label="Primary Career Profile",
            status="active",
            version=1,
            contact=ContactInfo(
                legal_name=None,
                primary_email=None,
            ),
            location=LocationInfo(),
        )
        self._profiles[default_id] = prof
        self._versions[default_id] = [
            ProfileVersionRecord(
                version=1,
                changed_fields=["initial_creation"],
                actor_id="system",
                reason="Default profile initialization",
            )
        ]

    # =========================================================================
    # Profile Lifecycle & Identity
    # =========================================================================

    def create_profile(
        self,
        req: ProfileCreateRequest,
        owner_id: str = "default_user",
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        ProfileAuthorizationEnforcer.check_permission(SCOPE_PROFILE_UPDATE, auth)
        prof_id = f"prof_{uuid4().hex[:12]}"
        prof = ApplicantProfile(
            id=prof_id,
            owner_id=owner_id,
            display_label=req.display_label,
            headline=req.headline,
            summary=req.summary,
            contact=req.contact or ContactInfo(),
            location=req.location or LocationInfo(),
            eligibility=req.eligibility,
            version=1,
        )
        self._profiles[prof_id] = prof
        self._versions[prof_id] = [
            ProfileVersionRecord(
                version=1,
                changed_fields=["create_profile"],
                actor_id=owner_id,
                reason="Profile created",
            )
        ]
        self._claim_registry.sync_from_profile(prof)
        return prof

    def get_profile(self, profile_id: str, auth: Optional[AuthContext] = None) -> ApplicantProfile:
        prof = self._profiles.get(profile_id)
        if not prof:
            raise ProfileNotFoundError(f"Applicant profile '{profile_id}' not found.")
        ProfileAuthorizationEnforcer.check_ownership(prof, auth)
        ProfileAuthorizationEnforcer.check_permission(SCOPE_PROFILE_READ, auth)
        return prof

    def get_primary_profile(self, auth: Optional[AuthContext] = None) -> ApplicantProfile:
        """Retrieves or creates the primary default applicant profile."""
        default_id = "prof_primary_applicant"
        if default_id not in self._profiles:
            self._init_default_profile()
        return self.get_profile(default_id, auth)

    def list_profiles(self, auth: Optional[AuthContext] = None) -> list[ApplicantProfile]:
        ProfileAuthorizationEnforcer.check_permission(SCOPE_PROFILE_READ, auth)
        profiles = list(self._profiles.values())
        if auth and not auth.is_admin and auth.client_id not in ("system", "supervisor_agent"):
            profiles = [p for p in profiles if p.owner_id in (auth.client_id, "default_user")]
        return profiles

    async def update_profile(
        self,
        profile_id: str,
        req: ProfileUpdateRequest,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        ProfileAuthorizationEnforcer.check_permission(SCOPE_PROFILE_UPDATE, auth)

        changed: list[str] = []
        if req.display_label is not None and req.display_label != prof.display_label:
            prof.display_label = req.display_label
            changed.append("display_label")
        if req.headline is not None and req.headline != prof.headline:
            prof.headline = req.headline
            changed.append("headline")
        if req.summary is not None and req.summary != prof.summary:
            prof.summary = req.summary
            changed.append("summary")
        if req.status is not None and req.status != prof.status:
            prof.status = req.status
            changed.append("status")
        if req.preferred_language is not None:
            prof.preferred_language = req.preferred_language
            changed.append("preferred_language")
        if req.contact is not None:
            prof.contact = req.contact
            changed.append("contact")
        if req.location is not None:
            prof.location = req.location
            changed.append("location")
        if req.eligibility is not None:
            prof.eligibility = req.eligibility
            changed.append("eligibility")

        if changed:
            prof.version += 1
            prof.updated_at = datetime.now(UTC)
            actor = auth.client_id if auth else "user"
            self._versions.setdefault(profile_id, []).append(
                ProfileVersionRecord(
                    version=prof.version,
                    changed_fields=changed,
                    actor_id=actor,
                    reason=req.reason or "Profile update",
                )
            )
            self._claim_registry.sync_from_profile(prof)
            for f in changed:
                await ProfileMemorySync.invalidate_stale_memories(profile_id, f)

        return prof

    async def delete_profile(self, profile_id: str, auth: Optional[AuthContext] = None) -> bool:
        prof = self.get_profile(profile_id, auth)
        ProfileAuthorizationEnforcer.check_permission(SCOPE_PROFILE_DELETE, auth)

        del self._profiles[profile_id]
        self._versions.pop(profile_id, None)

        # Clean associated evidence
        ev_to_del = [ev_id for ev_id, ev in self._evidence.items() if ev.profile_id == profile_id]
        for ev_id in ev_to_del:
            del self._evidence[ev_id]

        await ProfileMemorySync.publish_event("applicant.profile_deleted", profile_id)
        return True

    # =========================================================================
    # Education CRUD
    # =========================================================================

    async def add_education(
        self, profile_id: str, edu: EducationRecord, auth: Optional[AuthContext] = None
    ) -> EducationRecord:
        prof = self.get_profile(profile_id, auth)
        edu.profile_id = profile_id
        prof.education.append(edu)
        prof.version += 1
        prof.updated_at = datetime.now(UTC)
        self._claim_registry.sync_from_profile(prof)
        await ProfileMemorySync.invalidate_stale_memories(profile_id, "education")
        return edu

    async def update_education(
        self, profile_id: str, edu_id: str, updated: EducationRecord, auth: Optional[AuthContext] = None
    ) -> EducationRecord:
        prof = self.get_profile(profile_id, auth)
        for i, existing in enumerate(prof.education):
            if existing.id == edu_id:
                updated.id = edu_id
                updated.profile_id = profile_id
                updated.updated_at = datetime.now(UTC)
                prof.education[i] = updated
                prof.version += 1
                prof.updated_at = datetime.now(UTC)
                self._claim_registry.sync_from_profile(prof)
                await ProfileMemorySync.invalidate_stale_memories(profile_id, "education")
                return updated
        raise ProfileNotFoundError(f"Education record '{edu_id}' not found in profile '{profile_id}'.")

    async def delete_education(self, profile_id: str, edu_id: str, auth: Optional[AuthContext] = None) -> bool:
        prof = self.get_profile(profile_id, auth)
        orig_len = len(prof.education)
        prof.education = [e for e in prof.education if e.id != edu_id]
        if len(prof.education) < orig_len:
            prof.version += 1
            prof.updated_at = datetime.now(UTC)
            self._claim_registry.sync_from_profile(prof)
            await ProfileMemorySync.invalidate_stale_memories(profile_id, "education")
            return True
        return False

    # =========================================================================
    # Experience & Internships CRUD
    # =========================================================================

    async def add_experience(
        self, profile_id: str, exp: EmploymentRecord, auth: Optional[AuthContext] = None
    ) -> EmploymentRecord:
        prof = self.get_profile(profile_id, auth)
        exp.profile_id = profile_id
        prof.experience.append(exp)
        prof.version += 1
        prof.updated_at = datetime.now(UTC)
        self._claim_registry.sync_from_profile(prof)
        await ProfileMemorySync.invalidate_stale_memories(profile_id, "experience")
        return exp

    async def update_experience(
        self, profile_id: str, exp_id: str, updated: EmploymentRecord, auth: Optional[AuthContext] = None
    ) -> EmploymentRecord:
        prof = self.get_profile(profile_id, auth)
        for i, existing in enumerate(prof.experience):
            if existing.id == exp_id:
                updated.id = exp_id
                updated.profile_id = profile_id
                updated.updated_at = datetime.now(UTC)
                prof.experience[i] = updated
                prof.version += 1
                prof.updated_at = datetime.now(UTC)
                self._claim_registry.sync_from_profile(prof)
                await ProfileMemorySync.invalidate_stale_memories(profile_id, "experience")
                return updated
        raise ProfileNotFoundError(f"Experience record '{exp_id}' not found.")

    async def delete_experience(self, profile_id: str, exp_id: str, auth: Optional[AuthContext] = None) -> bool:
        prof = self.get_profile(profile_id, auth)
        orig_len = len(prof.experience)
        prof.experience = [e for e in prof.experience if e.id != exp_id]
        if len(prof.experience) < orig_len:
            prof.version += 1
            prof.updated_at = datetime.now(UTC)
            self._claim_registry.sync_from_profile(prof)
            await ProfileMemorySync.invalidate_stale_memories(profile_id, "experience")
            return True
        return False

    # =========================================================================
    # Skills CRUD & Taxonomy
    # =========================================================================

    async def add_skill(self, profile_id: str, skill: SkillItem, auth: Optional[AuthContext] = None) -> SkillItem:
        prof = self.get_profile(profile_id, auth)
        skill.profile_id = profile_id
        skill.canonical_name = skill.canonical_name.lower().strip()
        # Avoid duplicate skill names
        for existing in prof.skills:
            if existing.canonical_name == skill.canonical_name:
                return existing
        prof.skills.append(skill)
        prof.version += 1
        prof.updated_at = datetime.now(UTC)
        self._claim_registry.sync_from_profile(prof)
        await ProfileMemorySync.invalidate_stale_memories(profile_id, "skills")
        return skill

    async def delete_skill(self, profile_id: str, skill_id: str, auth: Optional[AuthContext] = None) -> bool:
        prof = self.get_profile(profile_id, auth)
        orig_len = len(prof.skills)
        prof.skills = [s for s in prof.skills if s.id != skill_id]
        if len(prof.skills) < orig_len:
            prof.version += 1
            prof.updated_at = datetime.now(UTC)
            self._claim_registry.sync_from_profile(prof)
            await ProfileMemorySync.invalidate_stale_memories(profile_id, "skills")
            return True
        return False

    # =========================================================================
    # Projects CRUD
    # =========================================================================

    async def add_project(self, profile_id: str, prj: ProjectRecord, auth: Optional[AuthContext] = None) -> ProjectRecord:
        prof = self.get_profile(profile_id, auth)
        prj.profile_id = profile_id
        prof.projects.append(prj)
        prof.version += 1
        prof.updated_at = datetime.now(UTC)
        self._claim_registry.sync_from_profile(prof)
        await ProfileMemorySync.invalidate_stale_memories(profile_id, "projects")
        return prj

    async def delete_project(self, profile_id: str, project_id: str, auth: Optional[AuthContext] = None) -> bool:
        prof = self.get_profile(profile_id, auth)
        orig_len = len(prof.projects)
        prof.projects = [p for p in prof.projects if p.id != project_id]
        if len(prof.projects) < orig_len:
            prof.version += 1
            prof.updated_at = datetime.now(UTC)
            self._claim_registry.sync_from_profile(prof)
            await ProfileMemorySync.invalidate_stale_memories(profile_id, "projects")
            return True
        return False

    # =========================================================================
    # Certifications CRUD
    # =========================================================================

    async def add_certification(
        self, profile_id: str, cert: CertificationRecord, auth: Optional[AuthContext] = None
    ) -> CertificationRecord:
        prof = self.get_profile(profile_id, auth)
        cert.profile_id = profile_id
        prof.certifications.append(cert)
        prof.version += 1
        prof.updated_at = datetime.now(UTC)
        self._claim_registry.sync_from_profile(prof)
        await ProfileMemorySync.invalidate_stale_memories(profile_id, "certifications")
        return cert

    async def delete_certification(self, profile_id: str, cert_id: str, auth: Optional[AuthContext] = None) -> bool:
        prof = self.get_profile(profile_id, auth)
        orig_len = len(prof.certifications)
        prof.certifications = [c for c in prof.certifications if c.id != cert_id]
        if len(prof.certifications) < orig_len:
            prof.version += 1
            prof.updated_at = datetime.now(UTC)
            self._claim_registry.sync_from_profile(prof)
            await ProfileMemorySync.invalidate_stale_memories(profile_id, "certifications")
            return True
        return False

    # =========================================================================
    # Claims & Evidence Library
    # =========================================================================

    def list_claims(
        self,
        profile_id: str,
        category: Optional[ClaimCategory] = None,
        status: Optional[VerificationStatus] = None,
        auth: Optional[AuthContext] = None,
    ) -> list[ApplicantClaim]:
        self.get_profile(profile_id, auth)
        return self._claim_registry.list_claims(profile_id, category, status)

    async def confirm_claim(
        self, profile_id: str, claim_id: str, auth: Optional[AuthContext] = None
    ) -> ApplicantClaim:
        self.get_profile(profile_id, auth)
        claim = self._claim_registry.confirm_claim(claim_id)
        await ProfileMemorySync.publish_event("applicant.claim_confirmed", profile_id, {"claim_id": claim_id})
        return claim

    async def reject_claim(
        self, profile_id: str, claim_id: str, auth: Optional[AuthContext] = None
    ) -> ApplicantClaim:
        self.get_profile(profile_id, auth)
        claim = self._claim_registry.reject_claim(claim_id)
        await ProfileMemorySync.publish_event("applicant.claim_rejected", profile_id, {"claim_id": claim_id})
        return claim

    def list_conflicts(self, profile_id: str, auth: Optional[AuthContext] = None) -> list[ProfileConflict]:
        self.get_profile(profile_id, auth)
        return self._claim_registry.list_conflicts(profile_id)

    async def resolve_conflict(
        self, profile_id: str, conflict_id: str, accepted_claim_id: str, auth: Optional[AuthContext] = None
    ) -> ProfileConflict:
        self.get_profile(profile_id, auth)
        conf = self._claim_registry.resolve_conflict(conflict_id, accepted_claim_id)
        await ProfileMemorySync.publish_event("applicant.conflict_resolved", profile_id, {"conflict_id": conflict_id})
        return conf

    async def upload_evidence(
        self,
        profile_id: str,
        filename: str,
        content: bytes,
        source_category: str = "resume",
        auth: Optional[AuthContext] = None,
    ) -> EvidenceMetadata:
        self.get_profile(profile_id, auth)
        content_hash = DocumentParser.compute_sha256(content)

        ev_id = f"evd_{uuid4().hex[:12]}"
        storage_filename = f"{ev_id}_{Path(filename).name}"
        storage_path = self._evidence_dir / storage_filename
        storage_path.write_bytes(content)

        ev = EvidenceMetadata(
            evidence_id=ev_id,
            profile_id=profile_id,
            filename=filename,
            file_type=Path(filename).suffix.lstrip(".").lower() or "bin",
            file_size_bytes=len(content),
            content_hash=content_hash,
            storage_path=str(storage_path),
            source_category=source_category,
        )
        self._evidence[ev_id] = ev
        await ProfileMemorySync.publish_event("applicant.evidence_uploaded", profile_id, {"evidence_id": ev_id})
        return ev

    def list_evidence(self, profile_id: str, auth: Optional[AuthContext] = None) -> list[EvidenceMetadata]:
        self.get_profile(profile_id, auth)
        return [ev for ev in self._evidence.values() if ev.profile_id == profile_id]

    async def delete_evidence(self, profile_id: str, evidence_id: str, auth: Optional[AuthContext] = None) -> bool:
        self.get_profile(profile_id, auth)
        ev = self._evidence.get(evidence_id)
        if not ev or ev.profile_id != profile_id:
            raise EvidenceNotFoundError(f"Evidence '{evidence_id}' not found.")

        p = Path(ev.storage_path)
        if p.exists():
            p.unlink(missing_ok=True)
        del self._evidence[evidence_id]
        await ProfileMemorySync.publish_event("applicant.evidence_deleted", profile_id, {"evidence_id": evidence_id})
        return True

    # =========================================================================
    # Document Import Pipeline & Review Queue
    # =========================================================================

    async def start_import(
        self,
        profile_id: str,
        filename: str,
        content: bytes,
        auth: Optional[AuthContext] = None,
    ) -> ImportJob:
        prof = self.get_profile(profile_id, auth)
        text, content_hash, metadata = DocumentParser.parse_bytes(content, filename)

        # Upload as supporting evidence simultaneously
        await self.upload_evidence(profile_id, filename, content, source_category="imported_document", auth=auth)

        import_id = f"imp_{uuid4().hex[:12]}"
        job = ImportJob(
            import_id=import_id,
            profile_id=profile_id,
            filename=filename,
            file_type=Path(filename).suffix.lstrip(".").lower(),
            status=ImportStatus.EXTRACTING,
            raw_text_preview=text[:600],
        )
        self._imports[import_id] = job

        # Extract structured candidate entities
        candidates = await CandidateExtractor.extract(text, import_id, existing_profile=prof)
        job.extracted_candidates = candidates
        job.status = ImportStatus.REVIEW_READY
        job.completed_at = datetime.now(UTC)

        await ProfileMemorySync.publish_event("applicant.import_completed", profile_id, {"import_id": import_id})
        return job

    def get_import_job(self, import_id: str, auth: Optional[AuthContext] = None) -> ImportJob:
        job = self._imports.get(import_id)
        if not job:
            raise ImportJobNotFoundError(f"Import job '{import_id}' not found.")
        self.get_profile(job.profile_id, auth)
        return job

    async def review_candidate(
        self,
        import_id: str,
        candidate_id: str,
        action: str,  # accept, correct, reject
        corrected_value: Optional[Any] = None,
        auth: Optional[AuthContext] = None,
    ) -> ExtractionCandidate:
        job = self.get_import_job(import_id, auth)
        target_cand: Optional[ExtractionCandidate] = None
        for c in job.extracted_candidates:
            if c.candidate_id == candidate_id:
                target_cand = c
                break
        if not target_cand:
            raise ProfileNotFoundError(f"Candidate '{candidate_id}' not found in import '{import_id}'.")

        if action == "reject":
            target_cand.status = CandidateStatus.REJECTED
        elif action == "correct":
            target_cand.status = CandidateStatus.CORRECTED
            if corrected_value is not None:
                target_cand.proposed_value = corrected_value
            await self._commit_candidate_to_profile(job.profile_id, target_cand, auth=auth)
        elif action == "accept":
            target_cand.status = CandidateStatus.ACCEPTED
            await self._commit_candidate_to_profile(job.profile_id, target_cand, auth=auth)

        return target_cand

    async def _commit_candidate_to_profile(
        self, profile_id: str, cand: ExtractionCandidate, auth: Optional[AuthContext] = None
    ) -> None:
        """Commits reviewed candidate into canonical profile."""
        val = cand.proposed_value
        if cand.field_name == "contact.legal_name" and isinstance(val, str):
            await self.update_profile(profile_id, ProfileUpdateRequest(contact=ContactInfo(legal_name=val)), auth=auth)
        elif cand.field_name == "contact.primary_email" and isinstance(val, str):
            await self.update_profile(profile_id, ProfileUpdateRequest(contact=ContactInfo(primary_email=val)), auth=auth)
        elif cand.field_name == "contact.phone" and isinstance(val, str):
            await self.update_profile(profile_id, ProfileUpdateRequest(contact=ContactInfo(phone=val)), auth=auth)
        elif cand.category == ClaimCategory.SKILL and isinstance(val, dict):
            await self.add_skill(
                profile_id,
                SkillItem(
                    name=val.get("name", "Skill"),
                    canonical_name=val.get("canonical_name", "skill"),
                    category=SkillCategory(val.get("category", "programming_languages")),
                ),
                auth=auth,
            )
        elif cand.category == ClaimCategory.DEGREE and isinstance(val, dict):
            await self.add_education(
                profile_id,
                EducationRecord(
                    institution=val.get("institution", "University"),
                    degree=val.get("degree", "Degree"),
                    field_of_study=val.get("field_of_study", "Major"),
                    start_date=val.get("start_date"),
                    end_date=val.get("end_date"),
                ),
                auth=auth,
            )
        elif cand.category == ClaimCategory.EMPLOYMENT and isinstance(val, dict):
            await self.add_experience(
                profile_id,
                EmploymentRecord(
                    employer=val.get("employer", "Company"),
                    job_title=val.get("job_title", "Role"),
                    start_date=val.get("start_date", "2024"),
                    end_date=val.get("end_date"),
                ),
                auth=auth,
            )
        elif cand.category == ClaimCategory.CONTRIBUTION and isinstance(val, dict):
            await self.add_project(
                profile_id,
                ProjectRecord(
                    title=val.get("title", "Project"),
                    description=val.get("description", ""),
                ),
                auth=auth,
            )

    # =========================================================================
    # Quality & Snapshots
    # =========================================================================

    def evaluate_quality(self, profile_id: str, auth: Optional[AuthContext] = None) -> DataQualityReport:
        prof = self.get_profile(profile_id, auth)
        claims = self._claim_registry.list_claims(profile_id)
        return DataQualityEngine.evaluate(prof, claims)

    def create_snapshot(
        self,
        profile_id: str,
        target_agent: str,
        scopes: list[str],
        auth: Optional[AuthContext] = None,
    ) -> ProfileSnapshot:
        prof = self.get_profile(profile_id, auth)
        if target_agent == "job_matching_agent":
            return AgentProfileAdapter.get_job_matching_snapshot(prof)
        elif target_agent == "resume_agent":
            return AgentProfileAdapter.get_resume_snapshot(prof)
        elif target_agent == "application_agent":
            return AgentProfileAdapter.get_application_snapshot(prof)
        elif target_agent == "interview_prep_agent":
            return AgentProfileAdapter.get_interview_prep_snapshot(prof)

        # Generic filtered snapshot
        filtered: dict[str, Any] = {"profile_id": prof.id, "version": prof.version}
        if "skills" in scopes:
            filtered["skills"] = [s.model_dump() for s in prof.skills]
        if "education" in scopes:
            filtered["education"] = [e.model_dump() for e in prof.education]
        if "experience" in scopes:
            filtered["experience"] = [x.model_dump() for x in prof.experience]
        if "projects" in scopes:
            filtered["projects"] = [p.model_dump() for p in prof.projects]

        return ProfileSnapshot(
            profile_id=prof.id,
            version=prof.version,
            target_agent=target_agent,
            authorized_scopes=scopes,
            filtered_data=filtered,
        )

    def get_version_history(self, profile_id: str, auth: Optional[AuthContext] = None) -> list[ProfileVersionRecord]:
        self.get_profile(profile_id, auth)
        return self._versions.get(profile_id, [])

    def export_profile(self, profile_id: str, auth: Optional[AuthContext] = None) -> dict[str, Any]:
        ProfileAuthorizationEnforcer.check_permission(SCOPE_PROFILE_EXPORT, auth)
        prof = self.get_profile(profile_id, auth)
        return {
            "exported_at": datetime.now(UTC).isoformat(),
            "profile": prof.model_dump(),
            "claims": [c.model_dump() for c in self._claim_registry.list_claims(profile_id)],
            "quality": self.evaluate_quality(profile_id, auth).model_dump(),
        }


# Singleton service instance
applicant_profile_service = ApplicantProfileService()


def get_profile_service() -> ApplicantProfileService:
    """Returns the singleton instance of ApplicantProfileService."""
    return applicant_profile_service

