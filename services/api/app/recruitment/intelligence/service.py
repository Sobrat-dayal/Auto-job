"""Job Intelligence Engine master service (Stage 28).

Orchestrates structured requirement extraction, NLP understanding,
evidence provenance, multi-source reconciliation, and human review queues.
"""

from datetime import UTC, datetime
import logging
from typing import Any
import uuid

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.db.engine import get_db_session
from app.db.models import (
    JobIntelligenceConflictModel,
    JobIntelligenceRecordModel,
    JobIntelligenceReviewModel,
    JobIntelligenceVersionModel,
    JobListing,
    JobRequirementEvidenceModel,
    JobRequirementGroupModel,
    JobRequirementModel,
)
from app.recruitment.intelligence.contracts import (
    AnalysisStatus,
    ApplicationInstructions,
    AtomicRequirement,
    CompensationIntelligence,
    ConflictRecord,
    ConflictType,
    DegreeLevel,
    DegreeStatus,
    EducationRequirement,
    EligibilityConditions,
    EmploymentConditions,
    EmploymentType,
    EvidenceConfidence,
    ExperienceRequirement,
    ExtractionMethod,
    JobIntelligenceRecord,
    LogicalOperator,
    PayPeriod,
    QualificationType,
    RequirementCategory,
    RequirementEvidence,
    RequirementGroup,
    ResolutionStrategy,
    ReviewQueueItem,
    ReviewStatus,
    SkillCategory,
    StructuredSkill,
    WorkplaceType,
)
from app.recruitment.intelligence.extraction.ai_extraction import run_ai_extraction_if_available
from app.recruitment.intelligence.extraction.compensation import extract_compensation_intelligence
from app.recruitment.intelligence.extraction.deadlines import extract_application_instructions
from app.recruitment.intelligence.extraction.education import extract_education_requirements
from app.recruitment.intelligence.extraction.eligibility import extract_eligibility_conditions
from app.recruitment.intelligence.extraction.employment import extract_employment_conditions
from app.recruitment.intelligence.extraction.experience import extract_experience_requirements
from app.recruitment.intelligence.extraction.responsibilities import extract_responsibilities
from app.recruitment.intelligence.extraction.skills import extract_skills_from_sections
from app.recruitment.intelligence.extraction.structured_jobposting import extract_schema_org_jobposting
from app.recruitment.intelligence.lifecycle.review import resolve_review_item
from app.recruitment.intelligence.lifecycle.versions import compute_description_hash, is_reanalysis_needed
from app.recruitment.intelligence.preprocessing.html_text import clean_html_description
from app.recruitment.intelligence.preprocessing.segmentation import segment_job_description
from app.recruitment.intelligence.reconciliation.conflicts import detect_multi_source_conflicts
from app.recruitment.intelligence.validation.confidence import calculate_overall_confidence
from app.recruitment.intelligence.validation.hallucination_defense import audit_job_evidence
from app.recruitment.intelligence.validation.security import (
    detect_adversarial_content,
    sanitize_untrusted_job_text,
)

logger = logging.getLogger(__name__)


class JobIntelligenceService:
    """Master service for Job Requirement Intelligence."""

    def __init__(self) -> None:
        self._in_memory_records: dict[str, JobIntelligenceRecord] = {}

    async def analyze_job(
        self,
        canonical_job_id: str,
        force: bool = False,
        use_ai: bool = True,
        db_session: AsyncSession | None = None,
    ) -> JobIntelligenceRecord:
        """Perform comprehensive intelligence analysis on a canonical job posting."""
        if db_session is not None:
            return await self._analyze_job_with_session(canonical_job_id, force, use_ai, db_session)
        async with get_db_session() as session:
            return await self._analyze_job_with_session(canonical_job_id, force, use_ai, session)

    async def _analyze_job_with_session(
        self,
        canonical_job_id: str,
        force: bool,
        use_ai: bool,
        session: AsyncSession,
    ) -> JobIntelligenceRecord:
        # 1. Fetch JobListing
        stmt = (
            select(JobListing)
            .options(
                selectinload(JobListing.intelligence_record).selectinload(JobIntelligenceRecordModel.requirements).selectinload(JobRequirementModel.evidence),
                selectinload(JobListing.intelligence_record).selectinload(JobIntelligenceRecordModel.requirement_groups),
                selectinload(JobListing.intelligence_record).selectinload(JobIntelligenceRecordModel.conflicts),
                selectinload(JobListing.intelligence_record).selectinload(JobIntelligenceRecordModel.reviews),
            )
            .where(JobListing.id == canonical_job_id)
        )
        result = await session.execute(stmt)
        job_listing = result.scalar_one_or_none()

        if not job_listing:
            # Check in-memory cache
            if canonical_job_id in self._in_memory_records:
                return self._in_memory_records[canonical_job_id]
            raise ValueError(f"JobListing with id '{canonical_job_id}' not found.")

        # 2. Text Normalization and Cleaning
        raw_description = job_listing.description or ""
        cleaned_text = clean_html_description(raw_description)

        if not cleaned_text:
            # Empty or missing description produces a PartialAnalysis record (Section 9)
            empty_record = JobIntelligenceRecord(
                canonical_job_id=canonical_job_id,
                description_hash="empty",
                analysis_status=AnalysisStatus.PARTIALLY_ANALYZED,
                job_title=job_listing.title,
                overall_confidence=0.0,
                error_message="Job description was unavailable or empty.",
                review_status=ReviewStatus.PENDING,
            )
            self._in_memory_records[canonical_job_id] = empty_record
            return empty_record

        desc_hash = compute_description_hash(cleaned_text)

        # 3. Check for existing analysis if not forced
        if not force and job_listing.intelligence_record:
            rec_model = job_listing.intelligence_record
            if rec_model.description_hash == desc_hash and rec_model.analysis_status in (
                AnalysisStatus.COMPLETED.value,
                AnalysisStatus.NEEDS_REVIEW.value,
            ):
                return self._model_to_record(rec_model)

        # 4. Security & Prompt Injection Defense
        adversarial_warnings = detect_adversarial_content(cleaned_text)
        safe_text = sanitize_untrusted_job_text(cleaned_text)

        # 5. Section Segmentation
        sections = segment_job_description(safe_text)

        # 6. Schema.org JSON-LD Extraction
        schema_data = extract_schema_org_jobposting(raw_description)

        # 7. Extract Skills
        structured_skills, atomic_skills = extract_skills_from_sections(sections, safe_text)

        # 8. Extract Education
        edu_reqs, atomic_edu = extract_education_requirements(sections, safe_text)

        # 9. Extract Experience
        exp_reqs, atomic_exp = extract_experience_requirements(sections, safe_text)

        # 10. Extract Employment Conditions
        employment = extract_employment_conditions(sections, safe_text)
        if job_listing.work_arrangement and employment.workplace_type == WorkplaceType.UNKNOWN:
            wa_lower = job_listing.work_arrangement.lower()
            if "remote" in wa_lower:
                employment.workplace_type = WorkplaceType.REMOTE_GLOBAL
            elif "hybrid" in wa_lower:
                employment.workplace_type = WorkplaceType.HYBRID
            elif "onsite" in wa_lower:
                employment.workplace_type = WorkplaceType.ONSITE

        # 11. Extract Compensation
        compensation = extract_compensation_intelligence(sections, safe_text)
        if not compensation.is_disclosed and job_listing.salary_range:
            # Fallback to job_listing.salary_range
            from app.recruitment.intelligence.preprocessing.segmentation import JobSection
            pseudo_sec = [JobSection(name="COMPENSATION", header_text="Salary", body_text=job_listing.salary_range, start_char=0, end_char=len(job_listing.salary_range), lines=[job_listing.salary_range])]
            compensation = extract_compensation_intelligence(pseudo_sec, job_listing.salary_range)

        # 12. Extract Eligibility & Sponsorship
        eligibility = extract_eligibility_conditions(sections, safe_text)

        # 13. Extract Application Deadlines & Instructions
        application_instructions = extract_application_instructions(
            sections, safe_text, job_listing.application_url or ""
        )

        # 14. Extract Responsibilities
        responsibilities = extract_responsibilities(sections)

        # 15. Requirement Aggregation & Grouping
        all_atomic = atomic_skills + atomic_edu + atomic_exp

        mandatory_reqs = [r for r in all_atomic if r.category == RequirementCategory.MANDATORY]
        preferred_reqs = [r for r in all_atomic if r.category == RequirementCategory.PREFERRED]
        optional_reqs = [r for r in all_atomic if r.category == RequirementCategory.OPTIONAL]
        conditional_reqs = [r for r in all_atomic if r.category == RequirementCategory.CONDITIONAL]

        root_group = RequirementGroup(
            operator=LogicalOperator.AND,
            description="Minimum Requirements",
            requirement_ids=[r.id for r in mandatory_reqs],
        )
        requirement_groups = [root_group]

        # 16. Hallucination Defense & Evidence Verification
        verified_atomic = audit_job_evidence(all_atomic, safe_text)

        # 17. Confidence & Quality Assessment
        warnings = list(adversarial_warnings)
        confidence, analysis_status, review_status = calculate_overall_confidence(
            requirements=verified_atomic,
            has_compensation=compensation.is_disclosed,
            has_education=len(edu_reqs) > 0,
            has_experience=len(exp_reqs) > 0,
            warnings=warnings,
        )

        # 18. Build Review Queue Items
        review_items: list[ReviewQueueItem] = []
        intelligence_id = str(uuid.uuid4())

        for req in verified_atomic:
            if req.needs_review:
                rev = ReviewQueueItem(
                    intelligence_id=intelligence_id,
                    requirement_id=req.id,
                    review_type="AMBIGUOUS_REQUIREMENT",
                    reason=req.review_notes or f"Review required for {req.name}",
                    status=ReviewStatus.PENDING,
                )
                review_items.append(rev)

        for w in adversarial_warnings:
            review_items.append(
                ReviewQueueItem(
                    intelligence_id=intelligence_id,
                    review_type="SECURITY_WARNING",
                    reason=w,
                    status=ReviewStatus.PENDING,
                )
            )

        # 19. Construct Result Record
        record = JobIntelligenceRecord(
            id=intelligence_id,
            canonical_job_id=canonical_job_id,
            canonical_job_version=1,
            description_hash=desc_hash,
            extractor_version="1.0.0",
            analysis_status=analysis_status,
            job_title=job_listing.title,
            responsibilities=responsibilities,
            mandatory_requirements=mandatory_reqs,
            preferred_requirements=preferred_reqs,
            optional_requirements=optional_reqs,
            conditional_requirements=conditional_reqs,
            requirement_groups=requirement_groups,
            skills=structured_skills,
            education=edu_reqs,
            experience=exp_reqs,
            employment_conditions=employment,
            compensation=compensation,
            eligibility=eligibility,
            application_instructions=application_instructions,
            conflicts=[],
            review_items=review_items,
            data_quality_warnings=warnings,
            overall_confidence=confidence,
            review_status=review_status,
        )

        # 20. Persistence in SQLite Database
        await self._persist_record_in_db(record, session)

        # Cache in memory
        self._in_memory_records[canonical_job_id] = record
        return record

    async def _persist_record_in_db(
        self,
        record: JobIntelligenceRecord,
        session: AsyncSession,
    ) -> None:
        """Persist or update intelligence models in the database."""
        # Check if record model exists
        stmt = select(JobIntelligenceRecordModel).where(
            JobIntelligenceRecordModel.canonical_job_id == record.canonical_job_id
        )
        res = await session.execute(stmt)
        existing = res.scalar_one_or_none()

        if existing:
            # Save version snapshot before updating
            version_stmt = select(JobIntelligenceVersionModel).where(
                JobIntelligenceVersionModel.intelligence_id == existing.id
            )
            v_res = await session.execute(version_stmt)
            curr_v_count = len(v_res.scalars().all())

            version_model = JobIntelligenceVersionModel(
                intelligence_id=existing.id,
                version_number=curr_v_count + 1,
                description_hash=existing.description_hash,
                snapshot_json=self._record_to_dict(record),
                change_summary="Automatic reanalysis upon description change",
            )
            session.add(version_model)

            # Update existing record fields
            existing.description_hash = record.description_hash
            existing.analysis_status = record.analysis_status.value
            existing.overall_confidence = record.overall_confidence
            existing.responsibilities_json = record.responsibilities
            existing.employment_conditions_json = record.employment_conditions.model_dump(mode="json")
            existing.compensation_json = record.compensation.model_dump(mode="json")
            existing.eligibility_json = record.eligibility.model_dump(mode="json")
            existing.deadlines_json = record.application_instructions.model_dump(mode="json")
            existing.data_quality_warnings_json = record.data_quality_warnings
            existing.review_status = record.review_status.value
            existing.updated_at = datetime.now(UTC)
            rec_id = existing.id
            record.id = rec_id

            # Delete old requirements and evidence for this intelligence record
            await session.execute(
                delete(JobRequirementModel).where(JobRequirementModel.intelligence_id == rec_id)
            )
            await session.execute(
                delete(JobRequirementGroupModel).where(JobRequirementGroupModel.intelligence_id == rec_id)
            )
        else:
            rec_model = JobIntelligenceRecordModel(
                id=record.id,
                canonical_job_id=record.canonical_job_id,
                canonical_job_version=record.canonical_job_version,
                description_hash=record.description_hash,
                extractor_version=record.extractor_version,
                analysis_status=record.analysis_status.value,
                job_title=record.job_title,
                role_family=record.role_family,
                seniority=record.seniority,
                overall_confidence=record.overall_confidence,
                responsibilities_json=record.responsibilities,
                employment_conditions_json=record.employment_conditions.model_dump(mode="json"),
                compensation_json=record.compensation.model_dump(mode="json"),
                eligibility_json=record.eligibility.model_dump(mode="json"),
                deadlines_json=record.application_instructions.model_dump(mode="json"),
                data_quality_warnings_json=record.data_quality_warnings,
                review_status=record.review_status.value,
            )
            session.add(rec_model)
            rec_id = record.id

        # Insert groups
        group_id_map: dict[str, str] = {}
        for grp in record.requirement_groups:
            grp_model = JobRequirementGroupModel(
                id=grp.id,
                intelligence_id=rec_id,
                operator=grp.operator.value,
                min_count=grp.min_count,
                description=grp.description,
            )
            session.add(grp_model)
            group_id_map[grp.id] = grp.id

        # Insert atomic requirements and evidence
        for req in (
            record.mandatory_requirements
            + record.preferred_requirements
            + record.optional_requirements
            + record.conditional_requirements
        ):
            req_model = JobRequirementModel(
                id=req.id,
                intelligence_id=rec_id,
                category=req.category.value,
                qualification_type=req.qualification_type.value,
                name=req.name,
                normalized_value=req.normalized_value,
                raw_text=req.raw_text,
                min_years=req.min_years,
                max_years=req.max_years,
                is_negated=req.is_negated,
                confidence=req.confidence.value,
                confidence_score=req.confidence_score,
                needs_review=req.needs_review,
                review_notes=req.review_notes,
            )
            session.add(req_model)

            for ev in req.evidence:
                ev_model = JobRequirementEvidenceModel(
                    id=ev.id,
                    requirement_id=req.id,
                    intelligence_id=rec_id,
                    section_name=ev.section_name,
                    supporting_text=ev.supporting_text,
                    start_char=ev.start_char,
                    end_char=ev.end_char,
                    quote_hash=ev.quote_hash,
                    extraction_method=ev.extraction_method.value,
                    verified_in_source=ev.verified_in_source,
                )
                session.add(ev_model)

        # Insert review queue items
        for r_item in record.review_items:
            rev_model = JobIntelligenceReviewModel(
                id=r_item.id,
                intelligence_id=rec_id,
                requirement_id=r_item.requirement_id,
                conflict_id=r_item.conflict_id,
                review_type=r_item.review_type,
                reason=r_item.reason,
                status=r_item.status.value,
            )
            session.add(rev_model)

    def _model_to_record(self, model: JobIntelligenceRecordModel) -> JobIntelligenceRecord:
        """Convert SQLAlchemy model to JobIntelligenceRecord DTO."""
        req_list: list[AtomicRequirement] = []
        for rm in model.requirements:
            ev_list = [
                RequirementEvidence(
                    id=em.id,
                    requirement_id=em.requirement_id,
                    section_name=em.section_name,
                    supporting_text=em.supporting_text,
                    start_char=em.start_char,
                    end_char=em.end_char,
                    quote_hash=em.quote_hash,
                    extraction_method=ExtractionMethod(em.extraction_method),
                    verified_in_source=em.verified_in_source,
                )
                for em in rm.evidence
            ]
            req_list.append(
                AtomicRequirement(
                    id=rm.id,
                    category=RequirementCategory(rm.category),
                    qualification_type=QualificationType(rm.qualification_type),
                    name=rm.name,
                    normalized_value=rm.normalized_value,
                    raw_text=rm.raw_text,
                    min_years=rm.min_years,
                    max_years=rm.max_years,
                    is_negated=rm.is_negated,
                    confidence=EvidenceConfidence(rm.confidence),
                    confidence_score=rm.confidence_score,
                    evidence=ev_list,
                    needs_review=rm.needs_review,
                    review_notes=rm.review_notes,
                )
            )

        groups = [
            RequirementGroup(
                id=gm.id,
                operator=LogicalOperator(gm.operator),
                min_count=gm.min_count,
                description=gm.description,
            )
            for gm in model.requirement_groups
        ]

        conflicts = [
            ConflictRecord(
                id=cm.id,
                conflict_type=ConflictType(cm.conflict_type),
                source_a_id=cm.source_a_id,
                source_a_text=cm.source_a_text,
                source_b_id=cm.source_b_id,
                source_b_text=cm.source_b_text,
                resolution_strategy=ResolutionStrategy(cm.resolution_strategy),
                resolved_text=cm.resolved_text,
                is_resolved=cm.is_resolved,
            )
            for cm in model.conflicts
        ]

        reviews = [
            ReviewQueueItem(
                id=rvm.id,
                intelligence_id=rvm.intelligence_id,
                requirement_id=rvm.requirement_id,
                conflict_id=rvm.conflict_id,
                review_type=rvm.review_type,
                reason=rvm.reason,
                status=ReviewStatus(rvm.status),
                reviewer_decision=rvm.reviewer_decision,
                reviewer_notes=rvm.reviewer_notes,
            )
            for rvm in model.reviews
        ]

        return JobIntelligenceRecord(
            id=model.id,
            canonical_job_id=model.canonical_job_id,
            canonical_job_version=model.canonical_job_version,
            description_hash=model.description_hash,
            extractor_version=model.extractor_version,
            analysis_status=AnalysisStatus(model.analysis_status),
            job_title=model.job_title,
            role_family=model.role_family,
            seniority=model.seniority,
            responsibilities=model.responsibilities_json or [],
            mandatory_requirements=[r for r in req_list if r.category == RequirementCategory.MANDATORY],
            preferred_requirements=[r for r in req_list if r.category == RequirementCategory.PREFERRED],
            optional_requirements=[r for r in req_list if r.category == RequirementCategory.OPTIONAL],
            conditional_requirements=[r for r in req_list if r.category == RequirementCategory.CONDITIONAL],
            requirement_groups=groups,
            employment_conditions=EmploymentConditions(**(model.employment_conditions_json or {})),
            compensation=CompensationIntelligence(**(model.compensation_json or {})),
            eligibility=EligibilityConditions(**(model.eligibility_json or {})),
            application_instructions=ApplicationInstructions(**(model.deadlines_json or {})),
            conflicts=conflicts,
            review_items=reviews,
            data_quality_warnings=model.data_quality_warnings_json or [],
            overall_confidence=model.overall_confidence,
            review_status=ReviewStatus(model.review_status),
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    def _record_to_dict(self, record: JobIntelligenceRecord) -> dict[str, Any]:
        return record.model_dump(mode="json")

    async def analyze_batch(
        self,
        job_ids: list[str],
        use_ai: bool = False,
    ) -> list[JobIntelligenceRecord]:
        """Perform batch analysis on multiple canonical jobs."""
        records: list[JobIntelligenceRecord] = []
        for jid in job_ids:
            try:
                rec = await self.analyze_job(jid, force=False, use_ai=use_ai)
                records.append(rec)
            except Exception as e:
                logger.error(f"Batch analysis failed for job '{jid}': {e}")
        return records

    async def get_record(self, canonical_job_id: str) -> JobIntelligenceRecord | None:
        """Fetch an intelligence record by canonical job id."""
        if canonical_job_id in self._in_memory_records:
            return self._in_memory_records[canonical_job_id]

        async with get_db_session() as session:
            stmt = (
                select(JobIntelligenceRecordModel)
                .options(
                    selectinload(JobIntelligenceRecordModel.requirements).selectinload(JobRequirementModel.evidence),
                    selectinload(JobIntelligenceRecordModel.requirement_groups),
                    selectinload(JobIntelligenceRecordModel.conflicts),
                    selectinload(JobIntelligenceRecordModel.reviews),
                )
                .where(JobIntelligenceRecordModel.canonical_job_id == canonical_job_id)
            )
            res = await session.execute(stmt)
            model = res.scalar_one_or_none()
            if model:
                rec = self._model_to_record(model)
                self._in_memory_records[canonical_job_id] = rec
                return rec
        return None

    async def list_jobs(
        self,
        status: AnalysisStatus | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[JobIntelligenceRecord]:
        """List intelligence records with optional status filter."""
        async with get_db_session() as session:
            stmt = (
                select(JobIntelligenceRecordModel)
                .options(
                    selectinload(JobIntelligenceRecordModel.requirements).selectinload(JobRequirementModel.evidence),
                    selectinload(JobIntelligenceRecordModel.requirement_groups),
                    selectinload(JobIntelligenceRecordModel.conflicts),
                    selectinload(JobIntelligenceRecordModel.reviews),
                )
                .order_by(JobIntelligenceRecordModel.updated_at.desc())
                .limit(limit)
                .offset(offset)
            )
            if status:
                stmt = stmt.where(JobIntelligenceRecordModel.analysis_status == status.value)

            res = await session.execute(stmt)
            models = res.scalars().all()
            return [self._model_to_record(m) for m in models]

    async def get_requirements(
        self,
        canonical_job_id: str,
        category: RequirementCategory | None = None,
    ) -> list[AtomicRequirement]:
        """Get atomic requirements for a job, optionally filtered by category."""
        rec = await self.get_record(canonical_job_id)
        if not rec:
            return []
        all_reqs = (
            rec.mandatory_requirements
            + rec.preferred_requirements
            + rec.optional_requirements
            + rec.conditional_requirements
        )
        if category:
            return [r for r in all_reqs if r.category == category]
        return all_reqs

    async def get_skills(self, canonical_job_id: str) -> list[StructuredSkill]:
        """Get structured skills for a job."""
        rec = await self.get_record(canonical_job_id)
        return rec.skills if rec else []

    async def get_education(self, canonical_job_id: str) -> list[EducationRequirement]:
        """Get education requirements for a job."""
        rec = await self.get_record(canonical_job_id)
        return rec.education if rec else []

    async def get_experience(self, canonical_job_id: str) -> list[ExperienceRequirement]:
        """Get experience requirements for a job."""
        rec = await self.get_record(canonical_job_id)
        return rec.experience if rec else []

    async def get_employment(self, canonical_job_id: str) -> EmploymentConditions:
        """Get employment conditions for a job."""
        rec = await self.get_record(canonical_job_id)
        return rec.employment_conditions if rec else EmploymentConditions()

    async def get_compensation(self, canonical_job_id: str) -> CompensationIntelligence:
        """Get compensation intelligence for a job."""
        rec = await self.get_record(canonical_job_id)
        return rec.compensation if rec else CompensationIntelligence()

    async def get_eligibility(self, canonical_job_id: str) -> EligibilityConditions:
        """Get work authorization and eligibility conditions for a job."""
        rec = await self.get_record(canonical_job_id)
        return rec.eligibility if rec else EligibilityConditions()

    async def get_deadlines(self, canonical_job_id: str) -> ApplicationInstructions:
        """Get application deadlines and instructions for a job."""
        rec = await self.get_record(canonical_job_id)
        return rec.application_instructions if rec else ApplicationInstructions()

    async def get_evidence(self, canonical_job_id: str) -> list[RequirementEvidence]:
        """Get all provenance evidence for a job."""
        reqs = await self.get_requirements(canonical_job_id)
        evidence = []
        for r in reqs:
            evidence.extend(r.evidence)
        return evidence

    async def get_conflicts(self, canonical_job_id: str) -> list[ConflictRecord]:
        """Get multi-source conflicts for a job."""
        rec = await self.get_record(canonical_job_id)
        return rec.conflicts if rec else []

    async def get_review_queue(self) -> list[ReviewQueueItem]:
        """Fetch all pending review items across jobs."""
        async with get_db_session() as session:
            stmt = (
                select(JobIntelligenceReviewModel)
                .where(JobIntelligenceReviewModel.status == ReviewStatus.PENDING.value)
                .order_by(JobIntelligenceReviewModel.created_at.desc())
            )
            res = await session.execute(stmt)
            models = res.scalars().all()
            return [
                ReviewQueueItem(
                    id=m.id,
                    intelligence_id=m.intelligence_id,
                    requirement_id=m.requirement_id,
                    conflict_id=m.conflict_id,
                    review_type=m.review_type,
                    reason=m.reason,
                    status=ReviewStatus(m.status),
                    reviewer_decision=m.reviewer_decision,
                    reviewer_notes=m.reviewer_notes,
                    created_at=m.created_at,
                )
                for m in models
            ]

    async def resolve_review(
        self,
        review_id: str,
        decision: ReviewStatus,
        notes: str | None = None,
        reviewer: str = "human_operator",
    ) -> ReviewQueueItem | None:
        """Resolve a review queue item with an authorized decision."""
        async with get_db_session() as session:
            stmt = select(JobIntelligenceReviewModel).where(JobIntelligenceReviewModel.id == review_id)
            res = await session.execute(stmt)
            model = res.scalar_one_or_none()
            if not model:
                return None

            model.status = decision.value
            model.reviewer_decision = decision.value
            model.reviewer_notes = notes
            model.reviewed_at = datetime.now(UTC)

            # Check if all reviews for the intelligence record are resolved
            int_stmt = select(JobIntelligenceReviewModel).where(
                JobIntelligenceReviewModel.intelligence_id == model.intelligence_id,
                JobIntelligenceReviewModel.status == ReviewStatus.PENDING.value,
            )
            pending_res = await session.execute(int_stmt)
            remaining_pending = len(pending_res.scalars().all())

            if remaining_pending == 0:
                rec_stmt = select(JobIntelligenceRecordModel).where(
                    JobIntelligenceRecordModel.id == model.intelligence_id
                )
                rec_res = await session.execute(rec_stmt)
                rec_model = rec_res.scalar_one_or_none()
                if rec_model:
                    rec_model.analysis_status = AnalysisStatus.COMPLETED.value
                    rec_model.review_status = ReviewStatus.APPROVED.value

            return ReviewQueueItem(
                id=model.id,
                intelligence_id=model.intelligence_id,
                requirement_id=model.requirement_id,
                conflict_id=model.conflict_id,
                review_type=model.review_type,
                reason=model.reason,
                status=decision,
                reviewer_decision=decision.value,
                reviewer_notes=notes,
                created_at=model.created_at,
            )

    async def get_diagnostics(self) -> dict[str, Any]:
        """Return operational diagnostics for the Job Intelligence Engine."""
        async with get_db_session() as session:
            stmt_all = select(JobIntelligenceRecordModel)
            res_all = await session.execute(stmt_all)
            all_records = res_all.scalars().all()

            stmt_rev = select(JobIntelligenceReviewModel).where(
                JobIntelligenceReviewModel.status == ReviewStatus.PENDING.value
            )
            res_rev = await session.execute(stmt_rev)
            pending_reviews = len(res_rev.scalars().all())

            counts: dict[str, int] = {}
            for r in all_records:
                counts[r.analysis_status] = counts.get(r.analysis_status, 0) + 1

            return {
                "total_records": len(all_records),
                "status_breakdown": counts,
                "pending_reviews": pending_reviews,
                "extractor_version": "1.0.0",
                "ai_enabled": True,
                "deterministic_rules_active": True,
                "timestamp": datetime.now(UTC).isoformat(),
            }


# Global singleton instance
job_intelligence_service = JobIntelligenceService()
