"""Deterministic ATS Readability & Structural Compliance Analyzer (Stage 23)."""

from __future__ import annotations

import logging
import re
from typing import Optional
from app.recruitment.resume.contracts import (
    ATSCheckResult,
    ATSCheckStatus,
    ATSReadabilityReport,
    ResumeDocument,
    SectionType,
)

logger = logging.getLogger("autonom.recruitment.resume.ats.readability")

STANDARD_ATS_HEADINGS: set[str] = {
    "education",
    "experience",
    "work experience",
    "employment",
    "skills",
    "technical skills",
    "projects",
    "certifications",
    "summary",
    "professional summary",
    "publications",
    "awards",
}


class ATSReadabilityAnalyzer:
    """Performs transparent, deterministic structural audits of resumes without fabricating ATS pass probabilities."""

    @classmethod
    def evaluate_document(
        cls,
        doc: ResumeDocument,
        extracted_text: Optional[str] = None,
    ) -> ATSReadabilityReport:
        checks: list[ATSCheckResult] = []

        # 1. Machine-Readable Text
        text_content = extracted_text if extracted_text is not None else cls._synthesize_text(doc)
        if len(text_content.strip()) > 100:
            checks.append(
                ATSCheckResult(
                    check_name="Machine-Readable Text",
                    status=ATSCheckStatus.PASS,
                    observed_evidence=f"Successfully extracted {len(text_content.strip().split())} words of direct text.",
                    impact_explanation="ATS parsers can ingest resume body text directly without requiring optical character recognition.",
                )
            )
        else:
            checks.append(
                ATSCheckResult(
                    check_name="Machine-Readable Text",
                    status=ATSCheckStatus.ERROR,
                    observed_evidence=f"Text content too short ({len(text_content.strip())} chars).",
                    impact_explanation="ATS parsers will likely fail to extract candidate qualifications.",
                    suggested_remediation="Ensure resume sections contain plain text rather than embedded image blocks.",
                )
            )

        # 2. Standard Section Headings
        headings_found = []
        non_standard_headings = []
        for sec in doc.sections:
            if sec.is_visible:
                clean_title = sec.display_title.lower().strip()
                headings_found.append(sec.display_title)
                if clean_title not in STANDARD_ATS_HEADINGS:
                    non_standard_headings.append(sec.display_title)

        if not non_standard_headings:
            checks.append(
                ATSCheckResult(
                    check_name="Standard Section Headings",
                    status=ATSCheckStatus.PASS,
                    observed_evidence=f"All {len(headings_found)} visible headings match standard ATS taxonomy: {', '.join(headings_found)}.",
                    impact_explanation="ATS category classifiers can accurately index education, experience, and skills without misclassification.",
                )
            )
        else:
            checks.append(
                ATSCheckResult(
                    check_name="Standard Section Headings",
                    status=ATSCheckStatus.WARNING,
                    observed_evidence=f"Non-standard heading(s) detected: {', '.join(non_standard_headings)}.",
                    impact_explanation="Some legacy ATS parsers may fail to categorize entries under non-standard headings.",
                    suggested_remediation="Consider renaming headings to standard variants (e.g. 'Work Experience' or 'Technical Skills').",
                )
            )

        # 3. Accessible Contact Information
        contact = doc.header_contact
        email = contact.get("primary_email") or ""
        phone = contact.get("phone") or ""
        has_email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", email))
        has_phone = bool(re.search(r"[\d+\-().\s]{7,}", phone))

        if has_email and has_phone:
            checks.append(
                ATSCheckResult(
                    check_name="Contact Information In Body",
                    status=ATSCheckStatus.PASS,
                    observed_evidence=f"Valid email ({email}) and phone number detected in document header body.",
                    impact_explanation="Recruiter outreach systems can automatically populate candidate contact details.",
                )
            )
        elif has_email:
            checks.append(
                ATSCheckResult(
                    check_name="Contact Information In Body",
                    status=ATSCheckStatus.WARNING,
                    observed_evidence=f"Email present ({email}), but phone number is missing or invalid.",
                    impact_explanation="Recruiters seeking phone screening may experience delays.",
                    suggested_remediation="Add a valid phone number with country/area code in contact settings.",
                )
            )
        else:
            checks.append(
                ATSCheckResult(
                    check_name="Contact Information In Body",
                    status=ATSCheckStatus.ERROR,
                    observed_evidence="Primary contact email is missing from the header.",
                    impact_explanation="Critical failure: ATS cannot map resume to applicant email account.",
                    suggested_remediation="Add a verified primary email in applicant profile contact info.",
                )
            )

        # 4. Chronological Consistency
        chrono_issues = []
        for sec in doc.sections:
            if sec.section_type in (SectionType.EXPERIENCE, SectionType.EDUCATION):
                for entry in sec.entries:
                    if entry.start_date and entry.end_date and entry.end_date != "Present":
                        if entry.start_date > entry.end_date:
                            chrono_issues.append(f"{entry.title} ({entry.start_date} > {entry.end_date})")

        if not chrono_issues:
            checks.append(
                ATSCheckResult(
                    check_name="Chronological Sanity",
                    status=ATSCheckStatus.PASS,
                    observed_evidence="All employment and educational date intervals are logically consistent.",
                    impact_explanation="Timeline parsers can determine total career duration and seniorities correctly.",
                )
            )
        else:
            checks.append(
                ATSCheckResult(
                    check_name="Chronological Sanity",
                    status=ATSCheckStatus.ERROR,
                    observed_evidence=f"Inverted date range(s): {', '.join(chrono_issues)}.",
                    impact_explanation="Chronology errors trigger parse failures or incorrect total experience calculations.",
                    suggested_remediation="Correct start/end dates so start date precedes end date.",
                )
            )

        # 5. Hyperlink Formatting
        links = []
        if contact.get("github_url"):
            links.append(contact["github_url"])
        if contact.get("linkedin_url"):
            links.append(contact["linkedin_url"])
        for sec in doc.sections:
            if sec.section_type == SectionType.PROJECTS:
                for entry in sec.entries:
                    for ref in entry.source_refs:
                        if ref.source_excerpt and "http" in ref.source_excerpt:
                            links.append(ref.source_excerpt)

        invalid_links = [l for l in links if not (l.startswith("http://") or l.startswith("https://") or l.startswith("github.com"))]
        if not invalid_links:
            checks.append(
                ATSCheckResult(
                    check_name="Hyperlink Accessibility",
                    status=ATSCheckStatus.PASS,
                    observed_evidence=f"Verified {len(links)} external link(s) use standard web protocols.",
                    impact_explanation="Recruiter interfaces can safely render clickable portfolio and repository links.",
                )
            )
        else:
            checks.append(
                ATSCheckResult(
                    check_name="Hyperlink Accessibility",
                    status=ATSCheckStatus.WARNING,
                    observed_evidence=f"Non-standard URL format: {', '.join(invalid_links)}.",
                    impact_explanation="Links may fail to open when clicked in ATS viewer panes.",
                    suggested_remediation="Prefix links with https://.",
                )
            )

        # Calculate counts
        passed_count = sum(1 for c in checks if c.status == ATSCheckStatus.PASS)
        warning_count = sum(1 for c in checks if c.status == ATSCheckStatus.WARNING)
        error_count = sum(1 for c in checks if c.status == ATSCheckStatus.ERROR)

        overall = ATSCheckStatus.PASS
        if error_count > 0:
            overall = ATSCheckStatus.ERROR
        elif warning_count > 0:
            overall = ATSCheckStatus.WARNING

        return ATSReadabilityReport(
            overall_status=overall,
            passed_count=passed_count,
            warning_count=warning_count,
            error_count=error_count,
            checks=checks,
            document_id=doc.id,
        )

    @classmethod
    def _synthesize_text(cls, doc: ResumeDocument) -> str:
        parts = [doc.header_contact.get("legal_name") or doc.title]
        for sec in doc.sections:
            if sec.is_visible:
                parts.append(sec.display_title)
                for entry in sec.entries:
                    parts.append(entry.title)
                    if entry.subtitle:
                        parts.append(entry.subtitle)
                    if entry.description:
                        parts.append(entry.description)
                    parts.extend(entry.bullet_points)
                    parts.extend(entry.tags)
        return " ".join(parts)
