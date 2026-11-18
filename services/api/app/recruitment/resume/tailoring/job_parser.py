"""Deterministic Job Description Parser & Requirements Extractor (Stage 23)."""

from __future__ import annotations

import logging
import re
from typing import Optional
from app.recruitment.resume.contracts import JobDescriptionSnapshot

logger = logging.getLogger("autonom.recruitment.resume.tailoring.job_parser")

TECH_KEYWORDS: list[str] = [
    "Python", "TypeScript", "JavaScript", "Rust", "Go", "Java", "C++", "C#", "SQL",
    "FastAPI", "React", "Next.js", "Django", "Flask", "Node.js", "Express", "NestJS",
    "PostgreSQL", "MySQL", "SQLite", "Redis", "MongoDB", "Elasticsearch",
    "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "CI/CD", "Linux",
    "PyTest", "Jest", "Vitest", "Playwright", "Git", "GitHub Actions",
    "PyTorch", "TensorFlow", "Hugging Face", "Scikit-Learn", "REST API", "GraphQL", "gRPC"
]


class JobDescriptionParser:
    """Parses raw job descriptions into structured requirements and technical criteria."""

    @classmethod
    def parse_job_description(
        cls,
        raw_text: str,
        job_title: Optional[str] = None,
        employer: Optional[str] = None,
        source_url: Optional[str] = None,
    ) -> JobDescriptionSnapshot:
        title = job_title or cls._extract_title(raw_text)
        comp = employer or cls._extract_employer(raw_text)

        required_skills: list[str] = []
        preferred_skills: list[str] = []
        responsibilities: list[str] = []
        tech_stack: list[str] = []

        # Find mentioned tech keywords
        text_lower = raw_text.lower()
        for tech in TECH_KEYWORDS:
            pattern = r"\b" + re.escape(tech.lower()) + r"\b"
            if re.search(pattern, text_lower):
                tech_stack.append(tech)

        # Categorize requirements based on section headings
        lines = raw_text.splitlines()
        current_section = "general"

        for line in lines:
            line_str = line.strip()
            if not line_str:
                continue

            lower_line = line_str.lower()
            if any(h in lower_line for h in ["requirement", "qualification", "what you need", "must have", "minimum"]):
                current_section = "required"
                continue
            elif any(h in lower_line for h in ["preferred", "nice to have", "bonus", "plus", "desired"]):
                current_section = "preferred"
                continue
            elif any(h in lower_line for h in ["responsibilit", "what you'll do", "the role", "duties"]):
                current_section = "responsibilities"
                continue
            elif line_str.endswith(":") and len(line_str) < 35:
                current_section = "general"
                continue

            # Process bulleted lines
            if line_str.startswith(("-", "*", "•")) or re.match(r"^\d+\.", line_str):
                clean_item = re.sub(r"^[-*•\d.]+\s*", "", line_str).strip()
                if len(clean_item) > 10:
                    if current_section == "required":
                        required_skills.append(clean_item)
                    elif current_section == "preferred":
                        preferred_skills.append(clean_item)
                    elif current_section == "responsibilities":
                        responsibilities.append(clean_item)

        # If bullets were not explicitly split by headings, divide tech stack into required
        if not required_skills and tech_stack:
            required_skills = [f"Proficiency in {t}" for t in tech_stack[:5]]

        return JobDescriptionSnapshot(
            job_title=title,
            employer=comp,
            raw_text=raw_text,
            required_skills=required_skills,
            preferred_skills=preferred_skills,
            responsibilities=responsibilities,
            tech_stack=tech_stack,
            source_url=source_url,
        )

    @classmethod
    def _extract_title(cls, text: str) -> str:
        lines = [line.strip() for line in text.splitlines() if line.strip()]
        if lines:
            first_line = lines[0]
            if len(first_line) < 60 and not any(c in first_line for c in [":", "http"]):
                return first_line
        # Fallback keyword scan
        for role in ["Backend Engineer", "Software Engineer", "Full Stack Developer", "AI Engineer", "Data Scientist", "DevOps Engineer"]:
            if re.search(r"\b" + re.escape(role) + r"\b", text, re.I):
                return role
        return "Software Engineer"

    @classmethod
    def _extract_employer(cls, text: str) -> Optional[str]:
        match = re.search(r"\b(?:at|with|join)\s+([A-Z][a-zA-Z0-9_\- ]{2,30})\b", text)
        if match:
            candidate = match.group(1).strip()
            if candidate.lower() not in ("our", "the", "a", "an", "this"):
                return candidate
        return None
