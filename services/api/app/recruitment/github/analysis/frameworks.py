"""Framework, Database, and DevOps Technology Classifier (Stage 22)."""

from __future__ import annotations

import logging
from typing import Optional

from app.recruitment.github.contracts import DetectionConfidence, TechCategory, TechnologyFinding

logger = logging.getLogger("autonom.recruitment.github.analysis.frameworks")

FRAMEWORK_TAXONOMY: dict[str, tuple[str, TechCategory]] = {
    # Backend Frameworks
    "fastapi": ("FastAPI", TechCategory.FRAMEWORK),
    "flask": ("Flask", TechCategory.FRAMEWORK),
    "django": ("Django", TechCategory.FRAMEWORK),
    "express": ("Express.js", TechCategory.FRAMEWORK),
    "nestjs": ("NestJS", TechCategory.FRAMEWORK),
    "spring-boot": ("Spring Boot", TechCategory.FRAMEWORK),
    "actix-web": ("Actix Web", TechCategory.FRAMEWORK),
    "axum": ("Axum", TechCategory.FRAMEWORK),
    "gin": ("Gin", TechCategory.FRAMEWORK),
    "aspnetcore": ("ASP.NET Core", TechCategory.FRAMEWORK),
    # Frontend Frameworks
    "react": ("React", TechCategory.FRAMEWORK),
    "react-dom": ("React", TechCategory.FRAMEWORK),
    "next": ("Next.js", TechCategory.FRAMEWORK),
    "vue": ("Vue.js", TechCategory.FRAMEWORK),
    "nuxt": ("Nuxt.js", TechCategory.FRAMEWORK),
    "angular": ("Angular", TechCategory.FRAMEWORK),
    "svelte": ("Svelte", TechCategory.FRAMEWORK),
    "tailwindcss": ("Tailwind CSS", TechCategory.FRAMEWORK),
    # Databases & Storage
    "postgresql": ("PostgreSQL", TechCategory.DATABASE),
    "psycopg2": ("PostgreSQL", TechCategory.DATABASE),
    "asyncpg": ("PostgreSQL", TechCategory.DATABASE),
    "pg": ("PostgreSQL", TechCategory.DATABASE),
    "mysql": ("MySQL", TechCategory.DATABASE),
    "pymysql": ("MySQL", TechCategory.DATABASE),
    "sqlite3": ("SQLite", TechCategory.DATABASE),
    "redis": ("Redis", TechCategory.DATABASE),
    "mongodb": ("MongoDB", TechCategory.DATABASE),
    "pymongo": ("MongoDB", TechCategory.DATABASE),
    "mongoose": ("MongoDB", TechCategory.DATABASE),
    # ORMs
    "sqlalchemy": ("SQLAlchemy", TechCategory.ORM),
    "prisma": ("Prisma", TechCategory.ORM),
    "@prisma/client": ("Prisma", TechCategory.ORM),
    "typeorm": ("TypeORM", TechCategory.ORM),
    "tortoise-orm": ("Tortoise ORM", TechCategory.ORM),
    "diesel": ("Diesel", TechCategory.ORM),
    # Testing
    "pytest": ("PyTest", TechCategory.TESTING),
    "jest": ("Jest", TechCategory.TESTING),
    "vitest": ("Vitest", TechCategory.TESTING),
    "playwright": ("Playwright", TechCategory.TESTING),
    "cypress": ("Cypress", TechCategory.TESTING),
    "mocha": ("Mocha", TechCategory.TESTING),
    # AI & ML
    "torch": ("PyTorch", TechCategory.AI_ML),
    "pytorch": ("PyTorch", TechCategory.AI_ML),
    "tensorflow": ("TensorFlow", TechCategory.AI_ML),
    "scikit-learn": ("Scikit-Learn", TechCategory.AI_ML),
    "transformers": ("Hugging Face Transformers", TechCategory.AI_ML),
    "langchain": ("LangChain", TechCategory.AI_ML),
    "openai": ("OpenAI SDK", TechCategory.AI_ML),
    # Containerization & Cloud
    "docker": ("Docker", TechCategory.CONTAINERIZATION),
    "kubernetes": ("Kubernetes", TechCategory.CONTAINERIZATION),
}


class TechnologyClassifier:
    """Classifies raw package findings into canonical technology categories."""

    @classmethod
    def classify_findings(cls, findings: list[TechnologyFinding]) -> list[TechnologyFinding]:
        classified: list[TechnologyFinding] = []
        seen_canonical: set[str] = set()

        for f in findings:
            clean_name = f.canonical_name.lower().strip()
            short_canonical = clean_name.split("/")[-1]
            match_key = None
            if clean_name in FRAMEWORK_TAXONOMY:
                match_key = clean_name
            elif short_canonical in FRAMEWORK_TAXONOMY:
                match_key = short_canonical

            if match_key:
                display_name, category = FRAMEWORK_TAXONOMY[match_key]
                f.technology_name = display_name
                f.name = display_name
                f.category = category
                f.confidence = DetectionConfidence.STRONGLY_SUPPORTED

            # Prevent duplicate identical technology entries for same repository
            key = f"{f.repo_id}_{f.technology_name}_{f.category}"
            if key not in seen_canonical:
                seen_canonical.add(key)
                classified.append(f)

        return classified
