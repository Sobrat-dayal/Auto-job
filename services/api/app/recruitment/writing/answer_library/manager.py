"""Reusable Answer Library & Parameterized Template Engine (Stage 24)."""

from __future__ import annotations

import logging
import re
from datetime import UTC, datetime
from typing import Any, Optional
from uuid import uuid4
from app.recruitment.profile.contracts import ApplicantProfile
from app.recruitment.writing.contracts import (
    AnswerFreshnessStatus,
    AnswerLibraryEntry,
    AnswerType,
    QuestionCategory,
)
from app.recruitment.writing.errors import WritingDomainError

logger = logging.getLogger("autonom.recruitment.writing.answer_library.manager")


class AnswerLibraryManager:
    """Manages reusable, parameterized application answer templates with freshness tracking."""

    def __init__(self) -> None:
        self._entries: dict[str, AnswerLibraryEntry] = {}
        self._init_default_entries()

    def _init_default_entries(self) -> None:
        defaults = [
            AnswerLibraryEntry(
                id="lib_tech_exp_01",
                owner_id="default_user",
                title="Technology Experience Overview",
                category=QuestionCategory.TECHNICAL,
                parameterized_template="My hands-on experience with {technology} stems primarily from {project}, where I was responsible for {contribution}.",
                sample_resolved_text="My hands-on experience with Python stems primarily from distributed event streaming, where I was responsible for architecting message ingestion pipelines.",
                answer_type=AnswerType.FREE_TEXT,
                applicable_technologies=["Python", "FastAPI", "PostgreSQL", "Docker"],
                associated_project_ids=[],
                state="approved",
                version_number=1,
            ),
            AnswerLibraryEntry(
                id="lib_teamwork_01",
                owner_id="default_user",
                title="Cross-Functional Team Collaboration",
                category=QuestionCategory.BEHAVIORAL,
                parameterized_template="When collaborating on {project}, I prioritized clear interface definitions, peer code reviews, and structured documentation to ensure smooth integration with team members.",
                sample_resolved_text="When collaborating on backend microservices, I prioritized clear interface definitions, peer code reviews, and structured documentation to ensure smooth integration with team members.",
                answer_type=AnswerType.PARAGRAPH,
                applicable_technologies=[],
                associated_project_ids=[],
                state="approved",
                version_number=1,
            ),
            AnswerLibraryEntry(
                id="lib_problem_solve_01",
                owner_id="default_user",
                title="Systematic Problem Solving & Root Cause Analysis",
                category=QuestionCategory.BEHAVIORAL,
                parameterized_template="When confronted with complex runtime issues, I isolate minimal reproducible cases, analyze telemetry metrics, and implement defensive automated tests to eliminate recurring regressions.",
                sample_resolved_text="When confronted with complex runtime issues, I isolate minimal reproducible cases, analyze telemetry metrics, and implement defensive automated tests to eliminate recurring regressions.",
                answer_type=AnswerType.PARAGRAPH,
                applicable_technologies=[],
                associated_project_ids=[],
                state="approved",
                version_number=1,
            ),
        ]
        for d in defaults:
            self._entries[d.id] = d

    def list_entries(
        self,
        owner_id: str = "default_user",
        category: Optional[QuestionCategory] = None,
    ) -> list[AnswerLibraryEntry]:
        results = [e for e in self._entries.values() if e.owner_id == owner_id]
        if category:
            results = [e for e in results if e.category == category]
        return results

    def get_entry(self, entry_id: str) -> AnswerLibraryEntry:
        entry = self._entries.get(entry_id)
        if not entry:
            raise WritingDomainError(f"Answer library entry '{entry_id}' not found.")
        return entry

    def create_entry(
        self,
        title: str,
        category: QuestionCategory,
        parameterized_template: str,
        sample_resolved_text: str,
        answer_type: AnswerType = AnswerType.FREE_TEXT,
        applicable_technologies: Optional[list[str]] = None,
        associated_project_ids: Optional[list[str]] = None,
        owner_id: str = "default_user",
    ) -> AnswerLibraryEntry:
        entry = AnswerLibraryEntry(
            id=f"lib_{uuid4().hex[:8]}",
            owner_id=owner_id,
            title=title,
            category=category,
            parameterized_template=parameterized_template,
            sample_resolved_text=sample_resolved_text,
            answer_type=answer_type,
            applicable_technologies=applicable_technologies or [],
            associated_project_ids=associated_project_ids or [],
            state="approved",
            version_number=1,
        )
        self._entries[entry.id] = entry
        logger.info(f"Created AnswerLibraryEntry '{entry.id}' ('{entry.title}')")
        return entry

    def update_entry(
        self,
        entry_id: str,
        title: Optional[str] = None,
        parameterized_template: Optional[str] = None,
        sample_resolved_text: Optional[str] = None,
        state: Optional[str] = None,
    ) -> AnswerLibraryEntry:
        entry = self.get_entry(entry_id)
        if title is not None:
            entry.title = title
        if parameterized_template is not None:
            entry.parameterized_template = parameterized_template
            entry.version_number += 1
        if sample_resolved_text is not None:
            entry.sample_resolved_text = sample_resolved_text
        if state is not None:
            entry.state = state
        entry.updated_at = datetime.now(UTC)
        return entry

    def resolve_template(
        self,
        entry: AnswerLibraryEntry,
        parameters: dict[str, str],
        profile: Optional[ApplicantProfile] = None,
    ) -> str:
        """Resolves template parameters using verified profile context and prevents placeholder leaks."""
        text = entry.parameterized_template

        for k, v in parameters.items():
            text = text.replace(f"{{{k}}}", v)

        # Fallback for remaining unresolved placeholders using profile
        if "{" in text and profile:
            if "{technology}" in text and profile.skills:
                text = text.replace("{technology}", profile.skills[0].name)
            if "{project}" in text and profile.projects:
                text = text.replace("{project}", profile.projects[0].title)
            if "{contribution}" in text and profile.projects:
                contrib = profile.projects[0].applicant_contribution or "architecting core functionality"
                text = text.replace("{contribution}", contrib)

        # Clean any remaining placeholders with default text
        text = re.sub(r"\{[a-zA-Z0-9_]+\}", "verified technical execution", text)
        return text

    def check_freshness(
        self,
        profile: ApplicantProfile,
    ) -> dict[str, Any]:
        """Audits answer library against current profile facts and flags outdated answers."""
        confirmed_techs = {s.name.lower() for s in profile.skills}
        outdated_count = 0

        for entry in self._entries.values():
            if entry.applicable_technologies:
                # If entry references technologies not in confirmed skills, mark for review
                has_unverified = any(t.lower() not in confirmed_techs for t in entry.applicable_technologies)
                if has_unverified and entry.state == "approved":
                    entry.state = "needs_review"
                    outdated_count += 1

        return {
            "total_entries": len(self._entries),
            "outdated_count": outdated_count,
            "checked_at": datetime.now(UTC).isoformat(),
        }
