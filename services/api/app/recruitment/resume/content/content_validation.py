"""Content Validation & Unsupported Claim Detection Engine (Stage 23)."""

from __future__ import annotations

import logging
import re
from typing import Any
from app.recruitment.profile.contracts import AcademicStatus, ApplicantProfile
from app.recruitment.resume.contracts import ResumeDocument, SectionType

logger = logging.getLogger("autonom.recruitment.resume.content.content_validation")


class ContentValidationEngine:
    """Verifies factual integrity and detects unsupported claims or discrepancies in resumes."""

    @classmethod
    def validate_document(
        cls,
        doc: ResumeDocument,
        profile: ApplicantProfile,
    ) -> list[dict[str, Any]]:
        issues: list[dict[str, Any]] = []

        # 1. Graduation Status Check
        for edu in profile.education:
            edu_status = getattr(edu, "academic_status", getattr(edu, "status", None))
            if edu_status == AcademicStatus.CURRENTLY_ENROLLED or (edu.end_date and "2026" in edu.end_date or "2027" in edu.end_date):
                # Ensure no resume section claims "Graduated" or "Degree Completed" for this institution
                for sec in doc.sections:
                    if sec.section_type == SectionType.EDUCATION:
                        for entry in sec.entries:
                            if edu.institution and edu.institution.lower() in (entry.organization or "").lower():
                                text_to_check = f"{entry.title} {entry.description or ''} {' '.join(entry.bullet_points)}"
                                if "graduated" in text_to_check.lower() and "expected" not in text_to_check.lower():
                                    issues.append({
                                        "severity": "error",
                                        "code": "PREMATURE_GRADUATION_CLAIM",
                                        "message": f"Education entry for '{edu.institution}' indicates completion, but profile records it as In-Progress (Expected: {edu.end_date or 'Future'}).",
                                        "location": f"Education -> {entry.title}",
                                    })

        # 2. Chronological Ordering and Date Sanity
        for sec in doc.sections:
            if sec.section_type in (SectionType.EXPERIENCE, SectionType.EDUCATION):
                for entry in sec.entries:
                    if entry.start_date and entry.end_date and entry.end_date != "Present":
                        if entry.start_date > entry.end_date:
                            issues.append({
                                "severity": "warning",
                                "code": "CHRONOLOGY_INVERSION",
                                "message": f"Start date '{entry.start_date}' is after end date '{entry.end_date}' for '{entry.title}'.",
                                "location": f"{sec.display_title} -> {entry.title}",
                            })

        # 3. Duplicate Bullet Points Detection
        seen_bullets: dict[str, str] = {}
        for sec in doc.sections:
            for entry in sec.entries:
                for b in entry.bullet_points:
                    clean = re.sub(r"\s+", " ", b.strip().lower())
                    if len(clean) > 20:
                        if clean in seen_bullets:
                            issues.append({
                                "severity": "warning",
                                "code": "DUPLICATE_BULLET",
                                "message": f"Identical bullet found in multiple entries: '{b[:50]}...'",
                                "location": f"{sec.display_title} -> {entry.title}",
                            })
                        else:
                            seen_bullets[clean] = entry.title

        # 4. Exaggerated / Invented Metrics Scan
        suspicious_metrics = re.compile(r"(\b(?:improved|increased|boosted|cut|reduced)\s+by\s+[5-9]\d{2,}%)", re.IGNORECASE)
        for sec in doc.sections:
            for entry in sec.entries:
                for b in entry.bullet_points:
                    match = suspicious_metrics.search(b)
                    if match:
                        issues.append({
                            "severity": "warning",
                            "code": "UNVERIFIED_EXTREME_METRIC",
                            "message": f"Suspiciously high unevidenced metric claim '{match.group(1)}'. Verify source empirical measurement.",
                            "location": f"{sec.display_title} -> {entry.title}",
                        })

        # 5. Unsupported Skills in Technical Sections
        profile_skill_names = {s.name.lower().strip() for s in profile.skills}
        for sec in doc.sections:
            if sec.section_type == SectionType.SKILLS:
                for entry in sec.entries:
                    for tag in entry.tags:
                        if tag.lower().strip() not in profile_skill_names:
                            # Flag skill if not anywhere in profile
                            issues.append({
                                "severity": "info",
                                "code": "UNSUPPORTED_SKILL_MENTION",
                                "message": f"Skill '{tag}' is not registered in the verified applicant profile skills catalog.",
                                "location": f"Skills -> {entry.title}",
                            })

        return issues
