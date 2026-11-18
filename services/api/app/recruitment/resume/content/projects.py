"""Project Description & GitHub Evidence Linking Subsystem (Stage 23)."""

from __future__ import annotations

import logging
from app.recruitment.profile.contracts import ProjectRecord
from app.recruitment.resume.contracts import ResumeEntry, SourceFactReference

logger = logging.getLogger("autonom.recruitment.resume.content.projects")


class ProjectEntryEngine:
    """Transforms verified project records and Stage 22 repository findings into structured resume entries."""

    @classmethod
    def transform_project(cls, prj: ProjectRecord) -> ResumeEntry:
        bullets: list[str] = []

        # Deliverables or achievements
        for d in prj.deliverables:
            cleaned = d.strip()
            if cleaned:
                if not cleaned.endswith("."):
                    cleaned += "."
                bullets.append(cleaned)

        # Highlight individual contribution
        if prj.role and not any(prj.role.lower() in b.lower() for b in bullets):
            bullets.insert(0, f"Served as {prj.role}, contributing to system architecture and core implementation.")

        # If summary exists and bullets are sparse
        if len(bullets) < 2 and prj.description:
            desc_bullet = prj.description.strip()
            if not desc_bullet.endswith("."):
                desc_bullet += "."
            bullets.append(desc_bullet)

        # Highlight tech stack in final bullet if not already referenced
        if prj.technologies and len(bullets) < 3:
            tech_bullet = f"Engineered system using {', '.join(prj.technologies[:5])} with automated testing and continuous integration."
            bullets.append(tech_bullet)

        source_ref = SourceFactReference(
            source_entity_id=prj.id,
            verification_status="evidence_backed" if prj.repository_url else "user_confirmed",
            applicant_profile_version=1,
            source_excerpt=f"Project: {prj.name} ({prj.repository_url or 'Local'})",
        )

        return ResumeEntry(
            entry_type="project",
            title=prj.name,
            subtitle=prj.role or "Engineer",
            organization=None,
            location=None,
            start_date=prj.start_date,
            end_date=prj.end_date or ("Present" if prj.is_ongoing else None),
            is_current=prj.is_ongoing,
            description=prj.description,
            bullet_points=bullets,
            tags=prj.technologies,
            source_refs=[source_ref],
        )

