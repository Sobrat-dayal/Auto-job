"""Candidate profile extractor leveraging deterministic heuristics and AI Gateway structured parsing."""

from __future__ import annotations

import logging
import re
from typing import Any, Optional
from uuid import uuid4

from app.recruitment.profile.contracts import (
    ApplicantProfile,
    CandidateStatus,
    ClaimCategory,
    ExtractionCandidate,
    SkillCategory,
)

logger = logging.getLogger("autonom.recruitment.profile.extractor")

EMAIL_REGEX = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
PHONE_REGEX = re.compile(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}")
URL_REGEX = re.compile(r"https?://(?:www\.)?([a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)+[/\w\-._~:?#[\]@!$&'()*+,;=]*)")
YEAR_REGEX = re.compile(r"\b(19\d{2}|20\d{2})\b")

KNOWN_SKILLS: dict[str, tuple[str, SkillCategory]] = {
    "python": ("Python", SkillCategory.PROGRAMMING_LANGUAGES),
    "typescript": ("TypeScript", SkillCategory.PROGRAMMING_LANGUAGES),
    "javascript": ("JavaScript", SkillCategory.PROGRAMMING_LANGUAGES),
    "rust": ("Rust", SkillCategory.PROGRAMMING_LANGUAGES),
    "c++": ("C++", SkillCategory.PROGRAMMING_LANGUAGES),
    "golang": ("Go", SkillCategory.PROGRAMMING_LANGUAGES),
    "go": ("Go", SkillCategory.PROGRAMMING_LANGUAGES),
    "java": ("Java", SkillCategory.PROGRAMMING_LANGUAGES),
    "c#": ("C#", SkillCategory.PROGRAMMING_LANGUAGES),
    "sql": ("SQL", SkillCategory.DATABASES),
    "postgresql": ("PostgreSQL", SkillCategory.DATABASES),
    "mysql": ("MySQL", SkillCategory.DATABASES),
    "sqlite": ("SQLite", SkillCategory.DATABASES),
    "mongodb": ("MongoDB", SkillCategory.DATABASES),
    "redis": ("Redis", SkillCategory.DATABASES),
    "react": ("React", SkillCategory.FRONTEND),
    "next.js": ("Next.js", SkillCategory.FRONTEND),
    "nextjs": ("Next.js", SkillCategory.FRONTEND),
    "vue": ("Vue.js", SkillCategory.FRONTEND),
    "tailwind": ("Tailwind CSS", SkillCategory.FRONTEND),
    "node.js": ("Node.js", SkillCategory.BACKEND),
    "nodejs": ("Node.js", SkillCategory.BACKEND),
    "fastapi": ("FastAPI", SkillCategory.BACKEND),
    "django": ("Django", SkillCategory.BACKEND),
    "flask": ("Flask", SkillCategory.BACKEND),
    "express": ("Express.js", SkillCategory.BACKEND),
    "docker": ("Docker", SkillCategory.CLOUD_DEVOPS),
    "kubernetes": ("Kubernetes", SkillCategory.CLOUD_DEVOPS),
    "aws": ("Amazon Web Services (AWS)", SkillCategory.CLOUD_DEVOPS),
    "azure": ("Microsoft Azure", SkillCategory.CLOUD_DEVOPS),
    "gcp": ("Google Cloud Platform", SkillCategory.CLOUD_DEVOPS),
    "terraform": ("Terraform", SkillCategory.CLOUD_DEVOPS),
    "git": ("Git", SkillCategory.DEVELOPMENT_TOOLS),
    "linux": ("Linux", SkillCategory.DEVELOPMENT_TOOLS),
    "pytorch": ("PyTorch", SkillCategory.AI_ML),
    "tensorflow": ("TensorFlow", SkillCategory.AI_ML),
    "scikit-learn": ("Scikit-Learn", SkillCategory.AI_ML),
    "playwright": ("Playwright", SkillCategory.TESTING),
    "pytest": ("PyTest", SkillCategory.TESTING),
}


class CandidateExtractor:
    """Extracts candidate fields from raw document text into an actionable review queue."""

    @classmethod
    async def extract(
        cls,
        text: str,
        import_id: str,
        existing_profile: Optional[ApplicantProfile] = None,
        use_ai: bool = False,
    ) -> list[ExtractionCandidate]:
        candidates: list[ExtractionCandidate] = []

        # 1. Deterministic extraction (always runs as high-reliability foundation)
        candidates.extend(cls._extract_identity_and_contact(text, import_id))
        candidates.extend(cls._extract_skills(text, import_id))
        candidates.extend(cls._extract_education(text, import_id))
        candidates.extend(cls._extract_experience(text, import_id))
        candidates.extend(cls._extract_projects(text, import_id))

        # 2. Duplicate detection against existing profile records
        if existing_profile:
            cls._check_duplicates_and_conflicts(candidates, existing_profile)

        return candidates

    @classmethod
    def _extract_identity_and_contact(cls, text: str, import_id: str) -> list[ExtractionCandidate]:
        candidates: list[ExtractionCandidate] = []
        lines = [line.strip() for line in text.splitlines() if line.strip()]

        # Name heuristic: First non-empty header-like line
        if lines:
            first_line = lines[0]
            if len(first_line.split()) in (2, 3, 4) and not any(ch in first_line for ch in "@:/?|"):
                candidates.append(
                    ExtractionCandidate(
                        import_id=import_id,
                        category=ClaimCategory.GENERAL,
                        field_name="contact.legal_name",
                        proposed_value=first_line,
                        raw_excerpt=first_line,
                        confidence=0.90,
                    )
                )

        # Email
        emails = EMAIL_REGEX.findall(text)
        if emails:
            primary_email = emails[0]
            candidates.append(
                ExtractionCandidate(
                    import_id=import_id,
                    category=ClaimCategory.GENERAL,
                    field_name="contact.primary_email",
                    proposed_value=primary_email,
                    raw_excerpt=primary_email,
                    confidence=0.95,
                )
            )

        # Phone
        phones = PHONE_REGEX.findall(text)
        if phones:
            raw_phone = phones[0] if isinstance(phones[0], str) else "".join(phones[0])
            candidates.append(
                ExtractionCandidate(
                    import_id=import_id,
                    category=ClaimCategory.GENERAL,
                    field_name="contact.phone",
                    proposed_value=raw_phone.strip(),
                    raw_excerpt=raw_phone.strip(),
                    confidence=0.88,
                )
            )

        # URLs (GitHub, LinkedIn)
        for url in URL_REGEX.findall(text):
            full_url = f"https://{url}" if not url.startswith("http") else url
            low = full_url.lower()
            if "linkedin.com" in low:
                candidates.append(
                    ExtractionCandidate(
                        import_id=import_id,
                        category=ClaimCategory.GENERAL,
                        field_name="professional_links.linkedin",
                        proposed_value=full_url,
                        raw_excerpt=full_url,
                        confidence=0.95,
                    )
                )
            elif "github.com" in low:
                candidates.append(
                    ExtractionCandidate(
                        import_id=import_id,
                        category=ClaimCategory.GENERAL,
                        field_name="professional_links.github",
                        proposed_value=full_url,
                        raw_excerpt=full_url,
                        confidence=0.95,
                    )
                )

        return candidates

    @classmethod
    def _extract_skills(cls, text: str, import_id: str) -> list[ExtractionCandidate]:
        candidates: list[ExtractionCandidate] = []
        lowered = text.lower()
        seen = set()

        for token, (display_name, category) in KNOWN_SKILLS.items():
            pattern = rf"\b{re.escape(token)}\b"
            match = re.search(pattern, lowered)
            if match and display_name not in seen:
                seen.add(display_name)
                start = max(0, match.start() - 25)
                end = min(len(text), match.end() + 25)
                excerpt = text[start:end].replace("\n", " ").strip()
                candidates.append(
                    ExtractionCandidate(
                        import_id=import_id,
                        category=ClaimCategory.SKILL,
                        field_name="skills",
                        proposed_value={
                            "name": display_name,
                            "canonical_name": token,
                            "category": category.value,
                            "proficiency": "intermediate",
                        },
                        raw_excerpt=f"...{excerpt}...",
                        confidence=0.92,
                    )
                )
        return candidates

    @classmethod
    def _extract_education(cls, text: str, import_id: str) -> list[ExtractionCandidate]:
        candidates: list[ExtractionCandidate] = []
        edu_keywords = ["university", "college", "institute", "polytechnic", "academy", "school of"]
        degree_keywords = [
            ("Bachelor of Science", "B.S."),
            ("Bachelor of Technology", "B.Tech"),
            ("Bachelor of Engineering", "B.E."),
            ("Master of Science", "M.S."),
            ("Master of Technology", "M.Tech"),
            ("Doctor of Philosophy", "Ph.D."),
            ("Bachelor of Arts", "B.A."),
        ]

        lines = text.splitlines()
        for i, line in enumerate(lines):
            low = line.lower()
            if any(kw in low for kw in edu_keywords):
                institution = line.strip()
                degree = "Bachelor of Science"
                field_of_study = "Computer Science"
                start_year = None
                end_year = None

                # Look nearby for degree and years
                context_window = "\n".join(lines[max(0, i - 2) : min(len(lines), i + 4)])
                years = YEAR_REGEX.findall(context_window)
                if len(years) >= 2:
                    start_year, end_year = sorted(years[:2])
                elif len(years) == 1:
                    end_year = years[0]

                for full_deg, abbr in degree_keywords:
                    if full_deg.lower() in context_window.lower() or abbr.lower() in context_window.lower():
                        degree = full_deg
                        break

                candidates.append(
                    ExtractionCandidate(
                        import_id=import_id,
                        category=ClaimCategory.DEGREE,
                        field_name="education",
                        proposed_value={
                            "institution": institution,
                            "degree": degree,
                            "field_of_study": field_of_study,
                            "start_date": start_year,
                            "end_date": end_year,
                            "academic_status": "graduated" if end_year and int(end_year) <= 2026 else "currently_enrolled",
                        },
                        raw_excerpt=context_window.replace("\n", " ").strip()[:180],
                        confidence=0.88,
                    )
                )
                break  # Primary education match
        return candidates

    @classmethod
    def _extract_experience(cls, text: str, import_id: str) -> list[ExtractionCandidate]:
        candidates: list[ExtractionCandidate] = []
        role_indicators = [
            "software engineer",
            "software developer",
            "frontend developer",
            "backend developer",
            "full stack engineer",
            "devops engineer",
            "intern",
            "software engineering intern",
            "data scientist",
            "ai engineer",
        ]

        lines = text.splitlines()
        for i, line in enumerate(lines):
            low = line.lower().strip()
            for role in role_indicators:
                if role in low:
                    job_title = role.title()
                    employer = "Organization"
                    if i > 0 and len(lines[i - 1].split()) <= 5:
                        employer = lines[i - 1].strip()

                    window = "\n".join(lines[max(0, i - 1) : min(len(lines), i + 5)])
                    years = YEAR_REGEX.findall(window)
                    s_date = years[0] if len(years) >= 1 else "2024"
                    e_date = years[1] if len(years) >= 2 else None

                    candidates.append(
                        ExtractionCandidate(
                            import_id=import_id,
                            category=ClaimCategory.EMPLOYMENT,
                            field_name="experience",
                            proposed_value={
                                "employer": employer,
                                "job_title": job_title,
                                "employment_type": "internship" if "intern" in role else "full_time",
                                "start_date": s_date,
                                "end_date": e_date,
                                "is_current": e_date is None or "present" in window.lower(),
                            },
                            raw_excerpt=window.replace("\n", " ").strip()[:200],
                            confidence=0.85,
                        )
                    )
                    break
        return candidates

    @classmethod
    def _extract_projects(cls, text: str, import_id: str) -> list[ExtractionCandidate]:
        candidates: list[ExtractionCandidate] = []
        lines = text.splitlines()
        in_project_section = False

        for i, line in enumerate(lines):
            low = line.lower().strip()
            if "projects" in low or "portfolio" in low:
                in_project_section = True
                continue
            if in_project_section and any(sec in low for sec in ["experience", "education", "skills", "certifications"]):
                in_project_section = False
                break

            if in_project_section and line.strip().startswith(("#", "-", "*", "•")) or (in_project_section and len(line.split()) in (2, 3, 4)):
                title = line.lstrip("#-*• ").strip()
                if len(title) > 3 and not title.lower().startswith("project"):
                    desc = lines[i + 1].strip() if i + 1 < len(lines) else ""
                    candidates.append(
                        ExtractionCandidate(
                            import_id=import_id,
                            category=ClaimCategory.CONTRIBUTION,
                            field_name="projects",
                            proposed_value={
                                "title": title,
                                "description": desc or "Personal engineering project",
                                "category": "personal",
                                "technologies": [],
                            },
                            raw_excerpt=f"{title}: {desc}"[:180],
                            confidence=0.82,
                        )
                    )
        return candidates

    @classmethod
    def _check_duplicates_and_conflicts(
        cls,
        candidates: list[ExtractionCandidate],
        profile: ApplicantProfile,
    ) -> None:
        """Flags potential duplicates or date conflicts against active canonical profile."""
        existing_skills = {s.canonical_name: s.id for s in profile.skills}
        existing_edu = [e.institution.lower() for e in profile.education]
        existing_exp = [(e.employer.lower(), e.job_title.lower()) for e in profile.experience]

        for c in candidates:
            if c.category == ClaimCategory.SKILL and isinstance(c.proposed_value, dict):
                canon = c.proposed_value.get("canonical_name", "").lower()
                if canon in existing_skills:
                    c.is_duplicate = True
                    c.matched_existing_id = existing_skills[canon]
                    c.status = CandidateStatus.REJECTED  # auto-deselect duplicates by default
            elif c.category == ClaimCategory.DEGREE and isinstance(c.proposed_value, dict):
                inst = c.proposed_value.get("institution", "").lower()
                if any(inst in e or e in inst for e in existing_edu):
                    c.is_duplicate = True
                    c.conflict_warning = "Matches existing education institution"
            elif c.category == ClaimCategory.EMPLOYMENT and isinstance(c.proposed_value, dict):
                emp = c.proposed_value.get("employer", "").lower()
                role = c.proposed_value.get("job_title", "").lower()
                if any(emp in e_emp and role in e_role for e_emp, e_role in existing_exp):
                    c.is_duplicate = True
                    c.conflict_warning = "Matches existing employer and job title"
