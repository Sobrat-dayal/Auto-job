"""Resume Content Prioritization Subsystem for Job Tailoring (Stage 23)."""

from __future__ import annotations

import logging
from app.recruitment.resume.contracts import (
    RequirementEvidenceMapping,
    RequirementMatchCategory,
    ResumeDocument,
    SectionType,
)

logger = logging.getLogger("autonom.recruitment.resume.tailoring.prioritization")


class ContentPrioritizationEngine:
    """Prioritizes verified skills, projects, and bullets to emphasize evidence matching the target role."""

    @classmethod
    def prioritize_resume(
        cls,
        doc: ResumeDocument,
        mappings: list[RequirementEvidenceMapping],
    ) -> ResumeDocument:
        # Collect supported matching keywords
        supported_keywords = {
            m.requirement_text.replace("Experience with ", "").lower().strip()
            for m in mappings
            if m.match_category in (RequirementMatchCategory.DIRECTLY_SUPPORTED, RequirementMatchCategory.PARTIALLY_SUPPORTED)
        }

        # 1. Prioritize Skills Section
        for sec in doc.sections:
            if sec.section_type == SectionType.SKILLS:
                for entry in sec.entries:
                    # Sort entry.tags: matching keywords first, then others
                    entry.tags.sort(
                        key=lambda t: (any(k in t.lower() for k in supported_keywords), t),
                        reverse=True,
                    )
                    # Rebuild formatted description line
                    entry.description = ", ".join(entry.tags)

        # 2. Prioritize Projects Section
        for sec in doc.sections:
            if sec.section_type == SectionType.PROJECTS:
                # Score each project based on number of matching keywords
                def project_score(entry) -> int:
                    score = 0
                    for tag in entry.tags:
                        if any(k in tag.lower() for k in supported_keywords):
                            score += 2
                    for b in entry.bullet_points:
                        if any(k in b.lower() for k in supported_keywords):
                            score += 1
                    return score

                sec.entries.sort(key=project_score, reverse=True)

        return doc
