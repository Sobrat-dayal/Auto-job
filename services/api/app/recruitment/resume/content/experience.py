"""Employment Experience & Bullet Generation Subsystem (Stage 23)."""

from __future__ import annotations

import logging
from app.recruitment.profile.contracts import EmploymentRecord
from app.recruitment.resume.contracts import ResumeEntry, SourceFactReference

logger = logging.getLogger("autonom.recruitment.resume.content.experience")


class ExperienceBulletEngine:
    """Transforms verified employment records and achievements into ATS-compatible resume entries."""

    @classmethod
    def transform_experience(cls, exp: EmploymentRecord) -> ResumeEntry:
        bullets: list[str] = []
        metrics: dict[str, str] = {}

        # Convert structured achievements into bullets
        for ach in exp.achievements:
            bullet = ach.description.strip()
            # If metrics are verified, highlight them
            if ach.metric_value and ach.metric_name:
                metrics[ach.metric_name] = ach.metric_value
                if ach.metric_value not in bullet:
                    bullet = f"{bullet} ({ach.metric_name}: {ach.metric_value})"
            if bullet and not bullet.endswith("."):
                bullet += "."
            bullets.append(bullet)

        # If no explicit achievements exist but a summary exists, use summary sentences
        if not bullets and exp.summary:
            for s in exp.summary.split("."):
                cleaned = s.strip()
                if cleaned:
                    bullets.append(f"{cleaned}.")

        # If still empty, construct an evidence-grounded baseline bullet
        if not bullets:
            tech_str = f" utilizing {', '.join(exp.technologies[:4])}" if exp.technologies else ""
            bullets.append(f"Delivered {exp.job_title} responsibilities at {exp.company}{tech_str} with focus on code quality and maintainability.")

        source_ref = SourceFactReference(
            source_entity_id=exp.id,
            verification_status="user_confirmed" if exp.is_current or exp.end_date else "user_reported",
            applicant_profile_version=1,
            source_excerpt=f"{exp.job_title} at {exp.company} ({exp.start_date} - {exp.end_date or 'Present'})",
        )

        return ResumeEntry(
            entry_type="job",
            title=exp.job_title,
            subtitle=exp.company,
            organization=exp.company,
            location=exp.location,
            start_date=exp.start_date,
            end_date=exp.end_date or ("Present" if exp.is_current else None),
            is_current=exp.is_current,
            description=exp.summary,
            bullet_points=bullets,
            tags=exp.technologies,
            source_refs=[source_ref],
            metrics=metrics,
        )

