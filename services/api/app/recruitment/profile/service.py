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
    ConcurrencyConflictError,
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
        req: Optional[ProfileCreateRequest] = None,
        display_label: Optional[str] = None,
        owner_id: str = "default_user",
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        ProfileAuthorizationEnforcer.check_permission(SCOPE_PROFILE_UPDATE, auth)
        if req is None:
            req = ProfileCreateRequest(display_label=display_label or "Default Profile")
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
        if auth and not getattr(auth, "is_admin", False) and auth.client_id not in ("system", "supervisor_agent", "admin", "autonom-desktop-local"):
            profiles = [p for p in profiles if p.owner_id in (auth.client_id, "default_user")]
        return profiles

    def update_profile_meta(
        self,
        profile_id: str,
        display_label: str,
        expected_version: Optional[int] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        ProfileAuthorizationEnforcer.check_permission(SCOPE_PROFILE_UPDATE, auth)
        if expected_version is not None and prof.version != expected_version:
            raise ConcurrencyConflictError(
                f"Version conflict: Expected version {expected_version}, but profile is at version {prof.version}."
            )
        prof.display_label = display_label
        prof.version += 1
        prof.updated_at = datetime.now(UTC)
        actor = auth.client_id if auth else "user"
        self._versions.setdefault(profile_id, []).append(
            ProfileVersionRecord(
                version=prof.version,
                changed_fields=["display_label"],
                actor_id=actor,
                reason="Updated profile display label",
            )
        )
        return prof

    def update_identity(
        self,
        profile_id: str,
        contact: Optional[ContactInfo] = None,
        location: Optional[LocationInfo] = None,
        eligibility: Optional[EmploymentEligibility] = None,
        expected_version: Optional[int] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        ProfileAuthorizationEnforcer.check_permission(SCOPE_PROFILE_UPDATE, auth)
        if expected_version is not None and prof.version != expected_version:
            raise ConcurrencyConflictError(
                f"Version conflict: Expected version {expected_version}, but profile is at version {prof.version}."
            )
        changed: list[str] = []
        if contact is not None:
            prof.contact = contact
            changed.append("contact")
        if location is not None:
            prof.location = location
            changed.append("location")
        if eligibility is not None:
            prof.eligibility = eligibility
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
                    reason="Updated profile identity",
                )
            )
            self._claim_registry.sync_from_profile(prof)
        return prof

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

    def delete_profile(self, profile_id: str, auth: Optional[AuthContext] = None) -> bool:
        prof = self.get_profile(profile_id, auth)
        ProfileAuthorizationEnforcer.check_permission(SCOPE_PROFILE_DELETE, auth)

        del self._profiles[profile_id]
        self._versions.pop(profile_id, None)

        # Clean associated evidence
        ev_to_del = [ev_id for ev_id, ev in self._evidence.items() if ev.profile_id == profile_id]
        for ev_id in ev_to_del:
            del self._evidence[ev_id]

        return True

    # =========================================================================
    # Education CRUD
    # =========================================================================

    def add_education(
        self,
        profile_id: str,
        edu_data: Optional[EducationRecord] = None,
        edu: Optional[EducationRecord] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        e = edu_data or edu
        if not e:
            return prof
        e.profile_id = profile_id
        prof.education.append(e)
        prof.version += 1
        prof.updated_at = datetime.now(UTC)
        self._claim_registry.sync_from_profile(prof)
        return prof

    def update_education(
        self,
        profile_id: str,
        education_id: Optional[str] = None,
        edu_id: Optional[str] = None,
        edu_data: Optional[EducationRecord] = None,
        updated: Optional[EducationRecord] = None,
        expected_version: Optional[int] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        target_id = education_id or edu_id
        target_data = edu_data or updated
        if expected_version is not None and prof.version != expected_version:
            raise ConcurrencyConflictError("Version conflict")
        for i, existing in enumerate(prof.education):
            if existing.id == target_id:
                if target_data:
                    target_data.id = target_id
                    target_data.profile_id = profile_id
                    prof.education[i] = target_data
                prof.version += 1
                prof.updated_at = datetime.now(UTC)
                self._claim_registry.sync_from_profile(prof)
                return prof
        raise ProfileNotFoundError(f"Education record '{target_id}' not found in profile '{profile_id}'.")

    def delete_education(
        self,
        profile_id: str,
        education_id: Optional[str] = None,
        edu_id: Optional[str] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        target_id = education_id or edu_id
        orig_len = len(prof.education)
        prof.education = [e for e in prof.education if e.id != target_id]
        if len(prof.education) < orig_len:
            prof.version += 1
            prof.updated_at = datetime.now(UTC)
            self._claim_registry.sync_from_profile(prof)
        return prof

    # =========================================================================
    # Experience & Internships CRUD
    # =========================================================================

    def add_experience(
        self,
        profile_id: str,
        exp: Optional[EmploymentRecord] = None,
        emp_data: Optional[EmploymentRecord] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        return self.add_employment(profile_id, emp_data=emp_data, exp=exp, auth=auth)

    def add_employment(
        self,
        profile_id: str,
        emp_data: Optional[EmploymentRecord] = None,
        exp: Optional[EmploymentRecord] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        e = emp_data or exp
        if not e:
            return prof
        e.profile_id = profile_id
        prof.experience.append(e)
        prof.version += 1
        prof.updated_at = datetime.now(UTC)
        self._claim_registry.sync_from_profile(prof)
        return prof

    def update_experience(
        self,
        profile_id: str,
        exp_id: Optional[str] = None,
        employment_id: Optional[str] = None,
        updated: Optional[EmploymentRecord] = None,
        emp_data: Optional[EmploymentRecord] = None,
        expected_version: Optional[int] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        return self.update_employment(
            profile_id=profile_id,
            employment_id=employment_id or exp_id,
            emp_data=emp_data or updated,
            expected_version=expected_version,
            auth=auth,
        )

    def update_employment(
        self,
        profile_id: str,
        employment_id: Optional[str] = None,
        exp_id: Optional[str] = None,
        emp_data: Optional[EmploymentRecord] = None,
        updated: Optional[EmploymentRecord] = None,
        expected_version: Optional[int] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        target_id = employment_id or exp_id
        target_data = emp_data or updated
        if expected_version is not None and prof.version != expected_version:
            raise ConcurrencyConflictError("Version conflict")
        for i, existing in enumerate(prof.experience):
            if existing.id == target_id:
                if target_data:
                    target_data.id = target_id
                    target_data.profile_id = profile_id
                    prof.experience[i] = target_data
                prof.version += 1
                prof.updated_at = datetime.now(UTC)
                self._claim_registry.sync_from_profile(prof)
                return prof
        raise ProfileNotFoundError(f"Experience record '{target_id}' not found.")

    def delete_experience(
        self,
        profile_id: str,
        exp_id: Optional[str] = None,
        employment_id: Optional[str] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        return self.delete_employment(profile_id, employment_id=employment_id or exp_id, auth=auth)

    def delete_employment(
        self,
        profile_id: str,
        employment_id: Optional[str] = None,
        exp_id: Optional[str] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        target_id = employment_id or exp_id
        orig_len = len(prof.experience)
        prof.experience = [e for e in prof.experience if e.id != target_id]
        if len(prof.experience) < orig_len:
            prof.version += 1
            prof.updated_at = datetime.now(UTC)
            self._claim_registry.sync_from_profile(prof)
        return prof

    # =========================================================================
    # Skills CRUD & Taxonomy
    # =========================================================================

    def add_skill(
        self,
        profile_id: str,
        skill: Optional[SkillItem] = None,
        skill_data: Optional[SkillItem] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        return self.add_or_update_skill(profile_id, skill_data=skill_data, skill=skill, auth=auth)

    def add_or_update_skill(
        self,
        profile_id: str,
        skill_data: Optional[SkillItem] = None,
        skill: Optional[SkillItem] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        s = skill_data or skill
        if not s:
            return prof
        s.profile_id = profile_id
        s.canonical_name = s.canonical_name.lower().strip()
        replaced = False
        for i, existing in enumerate(prof.skills):
            if existing.canonical_name == s.canonical_name or existing.id == s.id:
                prof.skills[i] = s
                replaced = True
                break
        if not replaced:
            prof.skills.append(s)
        prof.version += 1
        prof.updated_at = datetime.now(UTC)
        self._claim_registry.sync_from_profile(prof)
        return prof

    def delete_skill(
        self, profile_id: str, skill_id: str, auth: Optional[AuthContext] = None
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        orig_len = len(prof.skills)
        prof.skills = [s for s in prof.skills if s.id != skill_id]
        if len(prof.skills) < orig_len:
            prof.version += 1
            prof.updated_at = datetime.now(UTC)
            self._claim_registry.sync_from_profile(prof)
        return prof

    # =========================================================================
    # Projects CRUD
    # =========================================================================

    def add_project(
        self,
        profile_id: str,
        proj_data: Optional[ProjectRecord] = None,
        prj: Optional[ProjectRecord] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        p = proj_data or prj
        if not p:
            return prof
        p.profile_id = profile_id
        prof.projects.append(p)
        prof.version += 1
        prof.updated_at = datetime.now(UTC)
        self._claim_registry.sync_from_profile(prof)
        return prof

    def delete_project(
        self, profile_id: str, project_id: str, auth: Optional[AuthContext] = None
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        orig_len = len(prof.projects)
        prof.projects = [p for p in prof.projects if p.id != project_id]
        if len(prof.projects) < orig_len:
            prof.version += 1
            prof.updated_at = datetime.now(UTC)
            self._claim_registry.sync_from_profile(prof)
        return prof

    # =========================================================================
    # Certifications CRUD
    # =========================================================================

    def add_certification(
        self,
        profile_id: str,
        cert_data: Optional[CertificationRecord] = None,
        cert: Optional[CertificationRecord] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        c = cert_data or cert
        if not c:
            return prof
        c.profile_id = profile_id
        prof.certifications.append(c)
        prof.version += 1
        prof.updated_at = datetime.now(UTC)
        self._claim_registry.sync_from_profile(prof)
        return prof

    def delete_certification(
        self, profile_id: str, cert_id: str, auth: Optional[AuthContext] = None
    ) -> ApplicantProfile:
        prof = self.get_profile(profile_id, auth)
        orig_len = len(prof.certifications)
        prof.certifications = [c for c in prof.certifications if c.id != cert_id]
        if len(prof.certifications) < orig_len:
            prof.version += 1
            prof.updated_at = datetime.now(UTC)
            self._claim_registry.sync_from_profile(prof)
        return prof

    # =========================================================================
    # Claims & Evidence Library
    # =========================================================================

    def list_claims(
        self,
        profile_id: str,
        category: Optional[str] = None,
        status: Optional[str] = None,
        auth: Optional[AuthContext] = None,
    ) -> list[ApplicantClaim]:
        self.get_profile(profile_id, auth)
        cat_enum = ClaimCategory(category) if category else None
        stat_enum = VerificationStatus(status) if status else None
        return self._claim_registry.list_claims(profile_id, cat_enum, stat_enum)

    def confirm_claim(
        self,
        profile_id: str,
        claim_id: str,
        notes: Optional[str] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantClaim:
        self.get_profile(profile_id, auth)
        return self._claim_registry.confirm_claim(claim_id, notes=notes)

    def reject_claim(
        self,
        profile_id: str,
        claim_id: str,
        reason: Optional[str] = None,
        auth: Optional[AuthContext] = None,
    ) -> ApplicantClaim:
        self.get_profile(profile_id, auth)
        return self._claim_registry.reject_claim(claim_id, reason=reason)

    def list_conflicts(self, profile_id: str, auth: Optional[AuthContext] = None) -> list[ProfileConflict]:
        self.get_profile(profile_id, auth)
        return self._claim_registry.list_conflicts(profile_id)

    def resolve_conflict(
        self,
        profile_id: str,
        conflict_id: str,
        resolution_choice: str = "keep_a",
        chosen_claim_id: Optional[str] = None,
        manual_value: Optional[Any] = None,
        rationale: Optional[str] = None,
        accepted_claim_id: Optional[str] = None,
        auth: Optional[AuthContext] = None,
    ) -> ProfileConflict:
        self.get_profile(profile_id, auth)
        return self._claim_registry.resolve_conflict(
            conflict_id,
            accepted_claim_id=chosen_claim_id or accepted_claim_id,
            resolution_choice=resolution_choice,
            manual_value=manual_value,
            rationale=rationale,
        )

    def store_evidence(
        self,
        profile_id: str,
        filename: str,
        file_bytes: bytes,
        document_type: str = "resume",
        tags: Optional[list[str]] = None,
        auth: Optional[AuthContext] = None,
    ) -> EvidenceMetadata:
        self.get_profile(profile_id, auth)
        content_hash = DocumentParser.compute_sha256(file_bytes)

        ev_id = f"evd_{uuid4().hex[:12]}"
        storage_filename = f"{ev_id}_{Path(filename).name}"
        storage_path = self._evidence_dir / storage_filename
        storage_path.write_bytes(file_bytes)

        ev = EvidenceMetadata(
            evidence_id=ev_id,
            profile_id=profile_id,
            filename=filename,
            file_type=Path(filename).suffix.lstrip(".").lower() or "bin",
            file_size_bytes=len(file_bytes),
            content_hash=content_hash,
            storage_path=str(storage_path),
            source_category=document_type,
        )
        self._evidence[ev_id] = ev
        return ev

    async def upload_evidence(
        self,
        profile_id: str,
        filename: str,
        content: bytes,
        source_category: str = "resume",
        auth: Optional[AuthContext] = None,
    ) -> EvidenceMetadata:
        return self.store_evidence(
            profile_id=profile_id,
            filename=filename,
            file_bytes=content,
            document_type=source_category,
            auth=auth,
        )

    def list_evidence(self, profile_id: str, auth: Optional[AuthContext] = None) -> list[EvidenceMetadata]:
        self.get_profile(profile_id, auth)
        return [ev for ev in self._evidence.values() if ev.profile_id == profile_id]

    def delete_evidence(self, profile_id: str, evidence_id: str, auth: Optional[AuthContext] = None) -> bool:
        self.get_profile(profile_id, auth)
        ev = self._evidence.get(evidence_id)
        if not ev or ev.profile_id != profile_id:
            raise EvidenceNotFoundError(f"Evidence '{evidence_id}' not found.")

        p = Path(ev.storage_path)
        if p.exists():
            p.unlink(missing_ok=True)
        del self._evidence[evidence_id]
        return True

    # =========================================================================
    # Document Import Pipeline & Review Queue
    # =========================================================================

    def create_import_job(
        self,
        profile_id: str,
        filename: str,
        file_bytes: bytes,
        auth: Optional[AuthContext] = None,
    ) -> ImportJob:
        prof = self.get_profile(profile_id, auth)
        text, content_hash, metadata = DocumentParser.parse_bytes(file_bytes, filename)
        self.store_evidence(profile_id, filename, file_bytes, document_type="imported_document", auth=auth)

        import_id = f"imp_{uuid4().hex[:12]}"
        candidates: list[ExtractionCandidate] = []
        candidates.extend(CandidateExtractor._extract_identity_and_contact(text, import_id))
        candidates.extend(CandidateExtractor._extract_skills(text, import_id))
        candidates.extend(CandidateExtractor._extract_education(text, import_id))
        candidates.extend(CandidateExtractor._extract_experience(text, import_id))
        candidates.extend(CandidateExtractor._extract_projects(text, import_id))
        if prof:
            CandidateExtractor._check_duplicates_and_conflicts(candidates, prof)

        job = ImportJob(
            import_id=import_id,
            profile_id=profile_id,
            filename=filename,
            file_type=Path(filename).suffix.lstrip(".").lower() or "txt",
            status=ImportStatus.REVIEW_READY,
            extracted_candidates=candidates,
            raw_text_preview=text[:600],
            completed_at=datetime.now(UTC),
        )
        self._imports[import_id] = job
        return job

    async def start_import(
        self,
        profile_id: str,
        filename: str,
        content: bytes,
        auth: Optional[AuthContext] = None,
    ) -> ImportJob:
        return self.create_import_job(profile_id, filename, content, auth=auth)

    def get_import_job(
        self, import_id: str, auth: Optional[AuthContext] = None, profile_id: Optional[str] = None
    ) -> ImportJob:
        job = self._imports.get(import_id)
        if not job:
            raise ImportJobNotFoundError(f"Import job '{import_id}' not found.")
        self.get_profile(job.profile_id, auth)
        return job

    def review_candidate(
        self,
        import_id: str,
        candidate_id: str,
        action: str,  # accept, correct, reject
        corrected_value: Optional[Any] = None,
        auth: Optional[AuthContext] = None,
        profile_id: Optional[str] = None,
        modified_data: Optional[Any] = None,
        notes: Optional[str] = None,
    ) -> tuple[ExtractionCandidate, Optional[ApplicantClaim]]:
        job = self.get_import_job(import_id, auth)
        target_cand: Optional[ExtractionCandidate] = None
        for c in job.extracted_candidates:
            if c.candidate_id == candidate_id:
                target_cand = c
                break
        if not target_cand:
            raise ProfileNotFoundError(f"Candidate '{candidate_id}' not found in import '{import_id}'.")

        created_claim: Optional[ApplicantClaim] = None
        if action == "reject":
            target_cand.status = CandidateStatus.REJECTED
        elif action in ("correct", "modify"):
            target_cand.status = CandidateStatus.CORRECTED
            chosen_val = modified_data if modified_data is not None else corrected_value
            if chosen_val is not None:
                target_cand.proposed_value = chosen_val
            created_claim = self._commit_candidate_to_profile_sync(job.profile_id, target_cand, auth=auth)
        elif action == "accept":
            target_cand.status = CandidateStatus.ACCEPTED
            created_claim = self._commit_candidate_to_profile_sync(job.profile_id, target_cand, auth=auth)

        return target_cand, created_claim

    def _commit_candidate_to_profile_sync(
        self, profile_id: str, cand: ExtractionCandidate, auth: Optional[AuthContext] = None
    ) -> Optional[ApplicantClaim]:
        """Commits reviewed candidate into canonical profile."""
        val = cand.proposed_value
        prof = self.get_profile(profile_id, auth)
        if cand.field_name == "contact.legal_name" and isinstance(val, str):
            prof.contact.legal_name = val
            prof.version += 1
        elif cand.field_name == "contact.primary_email" and isinstance(val, str):
            prof.contact.primary_email = val
            prof.version += 1
        elif cand.field_name == "contact.phone" and isinstance(val, str):
            prof.contact.phone = val
            prof.version += 1
        elif cand.category == ClaimCategory.SKILL and isinstance(val, dict):
            self.add_or_update_skill(
                profile_id,
                SkillItem(
                    name=val.get("name", "Skill"),
                    canonical_name=val.get("canonical_name", "skill"),
                    category=SkillCategory(val.get("category", "programming_languages")),
                ),
                auth=auth,
            )
        elif cand.category == ClaimCategory.DEGREE and isinstance(val, dict):
            self.add_education(
                profile_id,
                edu_data=EducationRecord(
                    institution=val.get("institution", "University"),
                    degree=val.get("degree", "Degree"),
                    field_of_study=val.get("field_of_study", "Major"),
                    start_date=val.get("start_date"),
                    end_date=val.get("end_date"),
                ),
                auth=auth,
            )
        elif cand.category == ClaimCategory.EMPLOYMENT and isinstance(val, dict):
            self.add_employment(
                profile_id,
                emp_data=EmploymentRecord(
                    employer=val.get("employer", "Company"),
                    job_title=val.get("job_title", "Role"),
                    start_date=val.get("start_date", "2024"),
                    end_date=val.get("end_date"),
                ),
                auth=auth,
            )
        elif cand.category == ClaimCategory.CONTRIBUTION and isinstance(val, dict):
            self.add_project(
                profile_id,
                proj_data=ProjectRecord(
                    title=val.get("title", "Project"),
                    description=val.get("description", ""),
                ),
                auth=auth,
            )
        claims = self._claim_registry.sync_from_profile(prof)
        return claims[-1] if claims else None

    # =========================================================================
    # Quality, Snapshots, Versions, and Export
    # =========================================================================

    def evaluate_quality(self, profile_id: str, auth: Optional[AuthContext] = None) -> DataQualityReport:
        prof = self.get_profile(profile_id, auth)
        claims = self._claim_registry.list_claims(profile_id)
        return DataQualityEngine.evaluate(prof, claims)

    def generate_agent_snapshot(
        self,
        profile_id: str,
        target_agent: str,
        authorized_scopes: Optional[list[str]] = None,
        auth: Optional[AuthContext] = None,
    ) -> ProfileSnapshot:
        return self.create_snapshot(
            profile_id=profile_id,
            target_agent=target_agent,
            scopes=authorized_scopes or [],
            auth=auth,
        )

    def create_snapshot(
        self,
        profile_id: str,
        target_agent: str,
        scopes: list[str],
        auth: Optional[AuthContext] = None,
    ) -> ProfileSnapshot:
        prof = self.get_profile(profile_id, auth)
        target_norm = target_agent.lower().replace("_", "")
        if "jobmatching" in target_norm:
            snap = AgentProfileAdapter.get_job_matching_snapshot(prof)
            snap.target_agent = target_agent
            return snap
        elif "resume" in target_norm:
            snap = AgentProfileAdapter.get_resume_snapshot(prof)
            snap.target_agent = target_agent
            return snap
        elif "application" in target_norm:
            snap = AgentProfileAdapter.get_application_snapshot(prof)
            snap.target_agent = target_agent
            return snap
        elif "interview" in target_norm:
            snap = AgentProfileAdapter.get_interview_prep_snapshot(prof)
            snap.target_agent = target_agent
            return snap

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

