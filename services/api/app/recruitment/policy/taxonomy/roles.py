"""Role Taxonomy, Title Normalization, and Seniority Classifier (Stage 25)."""

from __future__ import annotations

import re
from typing import Optional
from app.recruitment.policy.contracts import RoleFamily, SeniorityLevel


# Standard keywords for role family classification
ROLE_FAMILY_KEYWORDS: dict[RoleFamily, list[str]] = {
    RoleFamily.BACKEND: [
        "backend", "back-end", "server", "api", "distributed systems", "platform",
        "microservices", "core engineering", "infrastructure developer"
    ],
    RoleFamily.FRONTEND: [
        "frontend", "front-end", "ui", "ux engineer", "web developer", "react", "vue", "angular", "client"
    ],
    RoleFamily.FULL_STACK: [
        "fullstack", "full-stack", "full stack", "software engineer", "software developer", "application developer"
    ],
    RoleFamily.AI_ML: [
        "machine learning", "ml engineer", "ai engineer", "deep learning", "nlp", "computer vision",
        "llm", "applied ai", "mles"
    ],
    RoleFamily.RESEARCH: [
        "research scientist", "ml researcher", "research fellow", "postdoc", "research engineer",
        "algorithm researcher", "scientific programmer"
    ],
    RoleFamily.DATA_ENGINEERING: [
        "data engineer", "etl", "data pipeline", "spark", "hadoop", "big data", "data platform"
    ],
    RoleFamily.DATA_SCIENCE: [
        "data scientist", "data science", "statistical modeler", "quantitative analyst"
    ],
    RoleFamily.CLOUD_DEVOPS: [
        "devops", "cloud engineer", "sre", "site reliability", "platform engineer",
        "kubernetes", "infrastructure engineer", "terraform"
    ],
    RoleFamily.CYBERSECURITY: [
        "security engineer", "cybersecurity", "infosec", "appsec", "penetration tester", "soc analyst"
    ],
    RoleFamily.MOBILE: [
        "android", "ios", "mobile engineer", "flutter", "react native", "swift", "kotlin"
    ],
    RoleFamily.SYSTEMS: [
        "embedded", "systems engineer", "firmware", "low level", "kernel", "c++", "rust systems"
    ],
}

# Explicit distinctions to prevent over-broadening
RESTRICTED_ROLE_DISTINCTIONS: list[tuple[str, str, str]] = [
    # (term_a, term_b, explanation)
    ("researcher", "operations", "Research focuses on theoretical and experimental modeling; Operations focuses on deployment pipelines and runtime reliability."),
    ("analyst", "scientist", "Data Analyst focuses on reporting, SQL queries, and BI visualization; Data Scientist builds predictive machine learning models."),
    ("manager", "entry_level", "Engineering Manager is people/delivery leadership and cannot be satisfied by entry-level qualifications."),
    ("intern", "senior", "Internship programs require current enrollment or early-career status, not senior tenure."),
]

SENIORITY_PATTERNS: list[tuple[SeniorityLevel, list[str]]] = [
    (SeniorityLevel.INTERNSHIP, ["intern", "internship", "summer analyst", "co-op", "student worker"]),
    (SeniorityLevel.APPRENTICE, ["apprentice", "apprenticeship"]),
    (SeniorityLevel.GRADUATE_TRAINEE, ["graduate trainee", "new grad", "campus hire", "university graduate", "associate"]),
    (SeniorityLevel.ENTRY_LEVEL, ["entry level", "entry-level", "junior", "jr", "software engineer i", "level 1", "e3", "l3"]),
    (SeniorityLevel.MID_LEVEL, ["software engineer ii", "level 2", "mid-level", "mid level", "e4", "l4", "swe ii"]),
    (SeniorityLevel.SENIOR, ["senior", "sr", "software engineer iii", "lead engineer", "e5", "l5", "tech lead"]),
    (SeniorityLevel.STAFF, ["staff", "principal", "distinguished", "architect", "fellow", "e6", "e7", "l6", "l7"]),
    (SeniorityLevel.MANAGEMENT, ["engineering manager", "team lead", "director", "vp of engineering", "head of engineering"]),
]


class RoleTaxonomyEngine:
    """Provides deterministic role classification, title normalization, and seniority detection."""

    @classmethod
    def classify_role_family(cls, title: str, description: Optional[str] = None) -> RoleFamily:
        """Classifies a job title into a canonical RoleFamily using deterministic keyword boundaries."""
        t_lower = title.lower()

        # Check explicit high-precedence research indicator
        if "research" in t_lower and ("scientist" in t_lower or "researcher" in t_lower):
            return RoleFamily.RESEARCH

        # Check explicit data distinctions
        if "data analyst" in t_lower:
            return RoleFamily.DATA_SCIENCE
        if "data engineer" in t_lower or "etl" in t_lower:
            return RoleFamily.DATA_ENGINEERING
        if "data scientist" in t_lower:
            return RoleFamily.DATA_SCIENCE

        # Check AI/ML
        if any(k in t_lower for k in ["machine learning", "ml engineer", "ai engineer", "deep learning"]):
            return RoleFamily.AI_ML

        # Check Backend vs Frontend vs DevOps
        if any(k in t_lower for k in ["devops", "sre", "cloud engineer", "site reliability"]):
            return RoleFamily.CLOUD_DEVOPS
        if any(k in t_lower for k in ["frontend", "front-end", "ui engineer", "react developer"]):
            return RoleFamily.FRONTEND
        if any(k in t_lower for k in ["backend", "back-end", "api engineer", "server engineer"]):
            return RoleFamily.BACKEND

        # Check Full Stack
        if "full stack" in t_lower or "fullstack" in t_lower:
            return RoleFamily.FULL_STACK

        # Check Systems / Embedded
        if any(k in t_lower for k in ["embedded", "firmware", "kernel", "systems engineer"]):
            return RoleFamily.SYSTEMS

        # Default fallback for generic software engineer
        if "software engineer" in t_lower or "software developer" in t_lower:
            return RoleFamily.BACKEND

        return RoleFamily.OTHER

    @classmethod
    def detect_seniority(cls, title: str, required_years: Optional[float] = None) -> SeniorityLevel:
        """Detects seniority level based on explicit title markers and required years."""
        t_lower = title.lower()

        # Check explicit keywords
        for level, keywords in SENIORITY_PATTERNS:
            for kw in keywords:
                # Use word-boundary check
                if re.search(rf"\b{re.escape(kw)}\b", t_lower):
                    return level

        # Fallback to required years if present
        if required_years is not None:
            if required_years <= 1.0:
                return SeniorityLevel.ENTRY_LEVEL
            elif required_years <= 3.5:
                return SeniorityLevel.MID_LEVEL
            elif required_years <= 7.0:
                return SeniorityLevel.SENIOR
            else:
                return SeniorityLevel.STAFF

        # Default standard assumption for software engineer without markers is mid-level
        return SeniorityLevel.MID_LEVEL

    @classmethod
    def check_role_distinction_violation(cls, preferred_title: str, candidate_title: str) -> Optional[str]:
        """Verifies whether candidate title conflates distinct specializations (e.g. Researcher vs Operations)."""
        pref = preferred_title.lower()
        cand = candidate_title.lower()

        for a, b, explanation in RESTRICTED_ROLE_DISTINCTIONS:
            if a in pref and b in cand:
                return f"Role conflict detected between '{preferred_title}' and '{candidate_title}': {explanation}"
            if b in pref and a in cand:
                return f"Role conflict detected between '{preferred_title}' and '{candidate_title}': {explanation}"

        return None
