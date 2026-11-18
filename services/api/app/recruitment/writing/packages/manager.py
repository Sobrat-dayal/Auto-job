"""Application Writing Package Assembly & Consistency Validator (Stage 24)."""

from __future__ import annotations

import logging
from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4
from app.recruitment.profile.contracts import ApplicantProfile
from app.recruitment.writing.contracts import (
    ApplicationQuestionSet,
    ApplicationWritingPackage,
    CoverLetterDocument,
    WritingPackageStatus,
)
from app.recruitment.writing.errors import (
    PackageNotReadyError,
    WritingDomainError,
)

logger = logging.getLogger("autonom.recruitment.writing.packages.manager")


class WritingPackageManager:
    """Assembles and validates comprehensive Application Writing Packages."""

    def __init__(self) -> None:
        self._packages: dict[str, ApplicationWritingPackage] = {}

    def list_packages(self, owner_id: str = "default_user") -> list[ApplicationWritingPackage]:
        return [p for p in self._packages.values() if p.owner_id == owner_id]

    def get_package(self, package_id: str) -> ApplicationWritingPackage:
        pkg = self._packages.get(package_id)
        if not pkg:
            raise WritingDomainError(f"Writing package '{package_id}' not found.")
        return pkg

    def create_package(
        self,
        target_job_title: str,
        target_employer: str,
        profile_snapshot_id: str,
        job_description_raw: Optional[str] = None,
        resume_id: Optional[str] = None,
        cover_letter_id: Optional[str] = None,
        question_set_id: Optional[str] = None,
        owner_id: str = "default_user",
    ) -> ApplicationWritingPackage:
        pkg = ApplicationWritingPackage(
            id=f"pkg_{uuid4().hex[:8]}",
            owner_id=owner_id,
            target_job_title=target_job_title,
            target_employer=target_employer,
            job_description_raw=job_description_raw,
            profile_snapshot_id=profile_snapshot_id,
            resume_id=resume_id,
            resume_version=1 if resume_id else None,
            cover_letter_id=cover_letter_id,
            cover_letter_version=1 if cover_letter_id else None,
            question_set_id=question_set_id,
            status=WritingPackageStatus.CREATED,
            version_number=1,
        )
        self._packages[pkg.id] = pkg
        logger.info(f"Created ApplicationWritingPackage '{pkg.id}' for '{target_job_title}' at '{target_employer}'")
        return pkg

    def validate_package(
        self,
        package: ApplicationWritingPackage,
        profile: ApplicantProfile,
        cover_letter: Optional[CoverLetterDocument] = None,
        question_set: Optional[ApplicationQuestionSet] = None,
    ) -> dict[str, Any]:
        """Validates consistency between cover letter, screening answers, and canonical profile."""
        issues: list[str] = []
        warnings: list[str] = []

        total_questions = 0
        answered_questions = 0
        pending_sensitive = 0
        pending_attestations = 0

        if question_set:
            total_questions = len(question_set.questions)
            for q in question_set.questions:
                ans = q.current_answer
                if ans and ans.answer_text.strip():
                    answered_questions += 1
                elif q.is_required:
                    issues.append(f"Required question '{q.exact_question_text[:40]}...' is unanswered.")

                if q.is_sensitive and (not ans or not ans.answer_text):
                    pending_sensitive += 1

                if q.requires_attestation and (not ans or not ans.user_attestation_timestamp):
                    pending_attestations += 1

        # Check Cover Letter consistency
        if cover_letter:
            cl_text = " ".join([b.text for b in cover_letter.blocks]).lower()
            if package.target_employer.lower() not in cl_text:
                warnings.append(f"Cover letter does not explicitly mention target employer '{package.target_employer}'.")

        package.total_questions = total_questions
        package.answered_questions = answered_questions
        package.pending_sensitive_decisions = pending_sensitive
        package.pending_attestations = pending_attestations
        package.is_ready_for_approval = (len(issues) == 0 and pending_attestations == 0)

        return {
            "package_id": package.id,
            "is_ready": package.is_ready_for_approval,
            "issues": issues,
            "warnings": warnings,
            "total_questions": total_questions,
            "answered_questions": answered_questions,
            "pending_attestations": pending_attestations,
        }

    def approve_package(
        self,
        package_id: str,
        actor_id: str = "default_user",
    ) -> ApplicationWritingPackage:
        pkg = self.get_package(package_id)
        if not pkg.is_ready_for_approval and pkg.pending_attestations > 0:
            raise PackageNotReadyError(
                f"Package '{package_id}' cannot be approved: pending {pkg.pending_attestations} required user attestations."
            )

        pkg.status = WritingPackageStatus.APPROVED
        pkg.approved_at = datetime.now(UTC)
        logger.info(f"WritingPackage '{package_id}' approved by '{actor_id}'. Ready for future application attachment.")
        return pkg
