"""Master Resume Intelligence Service Facade (Stage 23)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4
from app.core.security import AuthContext
from app.recruitment.profile.contracts import AcademicStatus, ApplicantProfile
from app.recruitment.profile.integrations.memory import ProfileMemorySync
from app.recruitment.profile.service import applicant_profile_service
from app.recruitment.resume.ats.readability import ATSReadabilityAnalyzer
from app.recruitment.resume.content.content_validation import ContentValidationEngine
from app.recruitment.resume.content.experience import ExperienceBulletEngine
from app.recruitment.resume.content.fact_selection import FactSelectionEngine
from app.recruitment.resume.content.profile_loader import ProfileSnapshotLoader
from app.recruitment.resume.content.projects import ProjectEntryEngine
from app.recruitment.resume.content.skills import SkillsOrganizationEngine
from app.recruitment.resume.content.summary import ProfessionalSummaryGenerator
from app.recruitment.resume.contracts import (
    ATSReadabilityReport,
    DocumentStatus,
    ExportArtifact,
    JobDescriptionParseRequest,
    JobDescriptionSnapshot,
    PageFormat,
    RequirementEvidenceMapping,
    ResumeCreateRequest,
    ResumeDocument,
    ResumeEntry,
    ResumeExportRequest,
    ResumeSection,
    ResumeTailorRequest,
    ResumeType,
    ResumeUpdateRequest,
    ResumeVersionRecord,
    SectionType,
    SourceFactReference,
)
from app.recruitment.resume.errors import (
    JobDescriptionNotFoundError,
    ResumeNotFoundError,
    ResumeValidationError,
)
from app.recruitment.resume.exports.manager import ExportManager
from app.recruitment.resume.portfolio.service import PortfolioService
from app.recruitment.resume.renderers.preview import DocumentPreviewEngine
from app.recruitment.resume.tailoring.evidence_matching import EvidenceMatchingEngine
from app.recruitment.resume.tailoring.job_parser import JobDescriptionParser
from app.recruitment.resume.tailoring.prioritization import ContentPrioritizationEngine
from app.recruitment.resume.templates.registry import ResumeTemplateRegistry
from app.recruitment.resume.versions.manager import ResumeVersionManager

logger = logging.getLogger("autonom.recruitment.resume.service")


class ResumeIntelligenceService:
    """Master service facade for resume synthesis, job tailoring, ATS audits, and document export."""

    def __init__(self) -> None:
        self.version_mgr = ResumeVersionManager()
        self.export_mgr = ExportManager()
        self.portfolio_svc = PortfolioService()

        # In-memory storage for resumes and job snapshots
        self._resumes: dict[str, ResumeDocument] = {}
        self._job_snapshots: dict[str, JobDescriptionSnapshot] = {}

    # =========================================================================
    # 1. Resume Document Lifecycle
    # =========================================================================

    def list_resumes(self, owner_id: str = "default_user") -> list[ResumeDocument]:
        return [r for r in self._resumes.values() if r.owner_id == owner_id]

    def get_resume(self, resume_id: str) -> ResumeDocument:
        res = self._resumes.get(resume_id)
        if not res:
            raise ResumeNotFoundError(f"Resume '{resume_id}' not found.")
        return res

    async def create_resume(
        self,
        req: ResumeCreateRequest,
        auth: Optional[AuthContext] = None,
    ) -> ResumeDocument:
        # Load profile and snapshot
        prof = ProfileSnapshotLoader.load_profile(req.profile_id, auth=auth)
        snapshot = ProfileSnapshotLoader.capture_snapshot(req.profile_id, auth=auth)

        # Contact info
        loc = prof.location if hasattr(prof, "location") and prof.location else None
        loc_str = ""
        if loc:
            parts = [p for p in [getattr(loc, "city", None), getattr(loc, "country", None)] if p]
            loc_str = ", ".join(parts)

        contact = {
            "legal_name": getattr(prof.contact, "legal_name", None) or "Applicant",
            "primary_email": getattr(prof.contact, "primary_email", None) or "",
            "phone": getattr(prof.contact, "phone", None) or "",
            "location": loc_str,
            "github_url": getattr(prof.contact, "github_url", getattr(prof.contact, "portfolio_url", "")) or "",
            "linkedin_url": getattr(prof.contact, "linkedin_url", "") or "",
        }

        # Build initial sections based on resume type
        sections: list[ResumeSection] = []
        sec_order = FactSelectionEngine.get_section_order(req.resume_type)

        ordering_idx = 0
        for sec_type in sec_order:
            if sec_type == SectionType.HEADER:
                continue

            elif sec_type == SectionType.SUMMARY:
                summary_text = ProfessionalSummaryGenerator.generate_summary(
                    prof, target_role=req.target_role, style="internship" if req.resume_type == ResumeType.INTERNSHIP else "standard"
                )
                sec = ResumeSection(
                    section_type=SectionType.SUMMARY,
                    display_title="Professional Summary",
                    ordering=ordering_idx,
                    entries=[
                        ResumeEntry(
                            entry_type="summary",
                            title="Summary",
                            description=summary_text,
                        )
                    ],
                )
                sections.append(sec)
                ordering_idx += 1

            elif sec_type == SectionType.EDUCATION:
                edu_records = FactSelectionEngine.filter_eligible_education(prof)
                entries = []
                for e in edu_records:
                    status = getattr(e, "academic_status", getattr(e, "status", None))
                    is_curr = status == AcademicStatus.CURRENTLY_ENROLLED or getattr(e, "is_current", False)
                    date_display = e.end_date or ("Expected " + (getattr(e, "expected_completion", None) or "2026") if is_curr else "Present")
                    gpa_val = getattr(e, "gpa", getattr(e, "grade_gpa", None))
                    entry = ResumeEntry(
                        entry_type="degree",
                        title=f"{e.degree or 'Degree'} in {e.field_of_study or 'Field'}",
                        subtitle=e.institution,
                        organization=e.institution,
                        location=getattr(e, "location", None),
                        start_date=e.start_date,
                        end_date=date_display,
                        is_current=is_curr,
                        description=f"GPA: {gpa_val}" if gpa_val else None,
                        bullet_points=[f"Relevant Coursework: {', '.join(e.coursework[:5])}"] if getattr(e, "coursework", None) else [],
                        source_refs=[SourceFactReference(source_entity_id=e.id, verification_status="user_confirmed")],
                    )
                    entries.append(entry)

                sec = ResumeSection(
                    section_type=SectionType.EDUCATION,
                    display_title="Education",
                    ordering=ordering_idx,
                    entries=entries,
                )
                sections.append(sec)
                ordering_idx += 1

            elif sec_type in (SectionType.EXPERIENCE, SectionType.INTERNSHIPS):
                exp_records = FactSelectionEngine.filter_eligible_experience(prof)
                entries = [ExperienceBulletEngine.transform_experience(x) for x in exp_records]
                sec = ResumeSection(
                    section_type=SectionType.EXPERIENCE,
                    display_title="Work Experience" if sec_type == SectionType.EXPERIENCE else "Internships",
                    ordering=ordering_idx,
                    entries=entries,
                )
                sections.append(sec)
                ordering_idx += 1

            elif sec_type == SectionType.PROJECTS:
                prj_records = FactSelectionEngine.filter_eligible_projects(prof, requested_ids=req.selected_project_ids)
                entries = [ProjectEntryEngine.transform_project(p) for p in prj_records]
                sec = ResumeSection(
                    section_type=SectionType.PROJECTS,
                    display_title="Technical Projects",
                    ordering=ordering_idx,
                    entries=entries,
                )
                sections.append(sec)
                ordering_idx += 1

            elif sec_type == SectionType.SKILLS:
                skills_records = FactSelectionEngine.filter_eligible_skills(prof, requested_names=req.selected_skill_names)
                entries = SkillsOrganizationEngine.group_skills(skills_records)
                sec = ResumeSection(
                    section_type=SectionType.SKILLS,
                    display_title="Technical Skills",
                    ordering=ordering_idx,
                    entries=entries,
                )
                sections.append(sec)
                ordering_idx += 1

            elif sec_type == SectionType.CERTIFICATIONS and prof.certifications:
                entries = [
                    ResumeEntry(
                        entry_type="certification",
                        title=getattr(c, "title", getattr(c, "name", "Certification")),
                        subtitle=getattr(c, "issuing_org", getattr(c, "issuing_organization", "")),
                        organization=getattr(c, "issuing_org", getattr(c, "issuing_organization", "")),
                        start_date=c.issue_date,
                        description=f"Credential ID: {c.credential_id}" if getattr(c, "credential_id", None) else None,
                        source_refs=[SourceFactReference(source_entity_id=c.id, verification_status="user_confirmed")],
                    )
                    for c in prof.certifications
                ]
                sec = ResumeSection(
                    section_type=SectionType.CERTIFICATIONS,
                    display_title="Certifications",
                    ordering=ordering_idx,
                    entries=entries,
                )
                sections.append(sec)
                ordering_idx += 1

        doc = ResumeDocument(
            owner_id=auth.client_id if auth else "default_user",
            profile_id=prof.id,
            profile_snapshot_id=f"snap_{uuid4().hex[:8]}",
            title=req.title,
            resume_type=req.resume_type,
            target_role=req.target_role,
            template_id=req.template_id,
            page_format=req.page_format,
            max_pages=req.max_pages,
            header_contact=contact,
            sections=sections,
            status=DocumentStatus.DRAFT,
        )

        # Handle optional job tailoring during creation
        if req.job_description_text:
            await self.tailor_resume(
                ResumeTailorRequest(
                    resume_id=doc.id,
                    job_description_text=req.job_description_text,
                    target_role=req.target_role,
                ),
                target_doc=doc,
            )

        self._resumes[doc.id] = doc
        logger.info(f"Created ResumeDocument: {doc.id} ('{doc.title}')")
        await ProfileMemorySync.publish_event("resume.created", doc.id, {"title": doc.title})
        return doc

    def update_resume(self, resume_id: str, req: ResumeUpdateRequest) -> ResumeDocument:
        doc = self.get_resume(resume_id)
        if req.title is not None:
            doc.title = req.title
        if req.target_role is not None:
            doc.target_role = req.target_role
        if req.template_id is not None:
            doc.template_id = req.template_id
        if req.page_format is not None:
            doc.page_format = req.page_format
        if req.max_pages is not None:
            doc.max_pages = req.max_pages
        if req.status is not None:
            doc.status = req.status
        if req.header_contact is not None:
            doc.header_contact = req.header_contact
        if req.sections is not None:
            doc.sections = req.sections

        doc.updated_at = datetime.now(UTC)
        return doc

    def delete_resume(self, resume_id: str) -> bool:
        self.get_resume(resume_id)
        del self._resumes[resume_id]
        logger.info(f"Deleted ResumeDocument: {resume_id}")
        return True

    def duplicate_resume(self, resume_id: str, new_title: Optional[str] = None) -> ResumeDocument:
        doc = self.get_resume(resume_id)
        cloned = doc.model_copy(deep=True)
        cloned.id = f"res_{uuid4().hex[:12]}"
        cloned.title = new_title or f"Copy of {doc.title}"
        cloned.status = DocumentStatus.DRAFT
        cloned.current_version = 1
        cloned.created_at = datetime.now(UTC)
        cloned.updated_at = datetime.now(UTC)
        cloned.approved_at = None
        cloned.approval_actor = None
        self._resumes[cloned.id] = cloned
        logger.info(f"Duplicated resume {doc.id} -> {cloned.id}")
        return cloned

    # =========================================================================
    # 2. Job Description Parsing & Tailoring
    # =========================================================================

    def parse_job_description(self, req: JobDescriptionParseRequest) -> JobDescriptionSnapshot:
        snap = JobDescriptionParser.parse_job_description(
            raw_text=req.raw_text,
            job_title=req.job_title,
            employer=req.employer,
            source_url=req.source_url,
        )
        self._job_snapshots[snap.id] = snap
        logger.info(f"Parsed JobDescription: {snap.id} ({snap.job_title} at {snap.employer or 'Unknown'})")
        return snap

    def get_job_snapshot(self, job_id: str) -> JobDescriptionSnapshot:
        snap = self._job_snapshots.get(job_id)
        if not snap:
            raise JobDescriptionNotFoundError(f"Job snapshot '{job_id}' not found.")
        return snap

    async def tailor_resume(
        self,
        req: ResumeTailorRequest,
        target_doc: Optional[ResumeDocument] = None,
    ) -> tuple[ResumeDocument, list[RequirementEvidenceMapping]]:
        doc = target_doc or self.get_resume(req.resume_id)

        # 1. Resolve Job Snapshot
        if req.job_id:
            job = self.get_job_snapshot(req.job_id)
        elif req.job_description_text:
            job = self.parse_job_description(JobDescriptionParseRequest(raw_text=req.job_description_text, job_title=req.target_role))
        else:
            raise ResumeValidationError("Tailoring requires either job_id or job_description_text.")

        doc.job_ref = job.id
        if req.target_role:
            doc.target_role = req.target_role

        # 2. Load Profile
        prof = ProfileSnapshotLoader.load_profile(doc.profile_id)

        # 3. Match Requirements
        mappings = EvidenceMatchingEngine.match_requirements(job, prof)

        # 4. Tailor Content & Prioritize
        ContentPrioritizationEngine.prioritize_resume(doc, mappings)

        # 5. Tailor Summary if requested
        if req.generate_summary:
            tailored_summary = ProfessionalSummaryGenerator.generate_summary(
                prof, target_role=doc.target_role or job.job_title
            )
            for sec in doc.sections:
                if sec.section_type == SectionType.SUMMARY:
                    sec.entries = [ResumeEntry(entry_type="summary", title="Summary", description=tailored_summary)]

        doc.updated_at = datetime.now(UTC)
        logger.info(f"Tailored resume {doc.id} against job {job.id} ({len(mappings)} criteria evaluated).")
        await ProfileMemorySync.publish_event("resume.tailoring_completed", doc.id, {"job_id": job.id})
        return doc, mappings

    # =========================================================================
    # 3. ATS Readability & Factual Validation
    # =========================================================================

    def evaluate_ats_readability(self, resume_id: str) -> ATSReadabilityReport:
        doc = self.get_resume(resume_id)
        return ATSReadabilityAnalyzer.evaluate_document(doc)

    def validate_factual_claims(self, resume_id: str) -> list[dict[str, Any]]:
        doc = self.get_resume(resume_id)
        prof = ProfileSnapshotLoader.load_profile(doc.profile_id)
        return ContentValidationEngine.validate_document(doc, prof)

    # =========================================================================
    # 4. Visual Preview
    # =========================================================================

    def generate_preview(self, resume_id: str) -> str:
        doc = self.get_resume(resume_id)
        template = ResumeTemplateRegistry.get_template(doc.template_id)
        return DocumentPreviewEngine.generate_html_preview(doc, template)

    # =========================================================================
    # 5. Approval & Version Snapshots
    # =========================================================================

    def approve_resume(self, resume_id: str, actor_id: str = "user") -> ResumeVersionRecord:
        doc = self.get_resume(resume_id)
        doc.status = DocumentStatus.APPROVED
        doc.approved_at = datetime.now(UTC)
        doc.approval_actor = actor_id

        # Record immutable version snapshot
        ver = self.version_mgr.create_version_snapshot(
            doc,
            actor_id=actor_id,
            changelog=f"Approved version v{doc.current_version}",
            is_published=True,
        )
        logger.info(f"Approved resume {doc.id}, recorded version v{ver.version_number}.")
        return ver

    # =========================================================================
    # 6. Document Export
    # =========================================================================

    def export_resume(self, resume_id: str, req: ResumeExportRequest) -> ExportArtifact:
        doc = self.get_resume(resume_id)
        artifact = self.export_mgr.export_resume(doc, req)

        # Attach artifact to current version if one exists
        versions = self.version_mgr.list_versions(doc.id)
        if versions:
            latest = versions[-1]
            latest.export_artifact_ids.append(artifact.export_id)

        return artifact


# Singleton master service instance
resume_intelligence_service = ResumeIntelligenceService()


def get_resume_service() -> ResumeIntelligenceService:
    """Returns the singleton instance of ResumeIntelligenceService."""
    return resume_intelligence_service
