"""Technical Skills Organization & Grouping Engine (Stage 23)."""

from __future__ import annotations

import logging
from app.recruitment.profile.contracts import SkillCategory, SkillItem
from app.recruitment.resume.contracts import ResumeEntry, SourceFactReference

logger = logging.getLogger("autonom.recruitment.resume.content.skills")


class SkillsOrganizationEngine:
    """Categorizes and formats verified skills into compact ATS-readable lines."""

    CATEGORY_MAP: dict[str, str] = {
        "programming_languages": "Languages",
        "frameworks": "Frameworks & Libraries",
        "databases": "Databases & Storage",
        "cloud_devops": "Cloud & DevOps",
        "tools": "Developer Tools & CI/CD",
        "ai_ml": "AI / Machine Learning",
        "testing": "Testing & Automation",
    }

    @classmethod
    def group_skills(cls, skills: list[SkillItem]) -> list[ResumeEntry]:
        grouped: dict[str, list[str]] = {
            "Languages": [],
            "Frameworks & Libraries": [],
            "Databases & Storage": [],
            "Cloud & DevOps": [],
            "Developer Tools": [],
            "Other Technical Skills": [],
        }

        for s in skills:
            name = s.name.strip()
            cat = s.category.value if hasattr(s.category, "value") else str(s.category)

            if cat in ("programming_languages", "languages") or name.lower() in ("python", "typescript", "javascript", "rust", "go", "sql", "c++", "c#", "java"):
                grouped["Languages"].append(name)
            elif cat in ("frameworks", "libraries") or name.lower() in ("fastapi", "react", "next.js", "django", "flask", "express", "pytorch", "tensorflow", "vue"):
                grouped["Frameworks & Libraries"].append(name)
            elif cat in ("databases", "storage") or name.lower() in ("postgresql", "sqlite", "mysql", "redis", "mongodb"):
                grouped["Databases & Storage"].append(name)
            elif cat in ("cloud_devops", "cloud", "devops") or name.lower() in ("docker", "kubernetes", "aws", "gcp", "azure", "git", "github actions", "linux"):
                grouped["Cloud & DevOps"].append(name)
            elif cat in ("tools", "testing") or name.lower() in ("pytest", "vitest", "jest", "playwright", "postman", "vite"):
                grouped["Developer Tools"].append(name)
            else:
                grouped["Other Technical Skills"].append(name)

        entries: list[ResumeEntry] = []
        for grp_name, items in grouped.items():
            if not items:
                continue
            # Remove duplicates preserving order
            seen: set[str] = set()
            deduped = [x for x in items if not (x.lower() in seen or seen.add(x.lower()))]
            skills_line = ", ".join(deduped)

            entries.append(
                ResumeEntry(
                    entry_type="skill_group",
                    title=grp_name,
                    subtitle=None,
                    description=skills_line,
                    tags=deduped,
                    bullet_points=[],
                )
            )

        return entries
