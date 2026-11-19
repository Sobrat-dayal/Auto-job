"""Technical and non-technical skill extraction and normalization against canonical taxonomy."""

import re

from app.recruitment.intelligence.contracts import (
    AtomicRequirement,
    EvidenceConfidence,
    ExtractionMethod,
    QualificationType,
    RequirementCategory,
    RequirementEvidence,
    SkillCategory,
    StructuredSkill,
)
from app.recruitment.intelligence.extraction.requirement_logic import is_skill_negated
from app.recruitment.intelligence.preprocessing.segmentation import JobSection
from app.recruitment.intelligence.preprocessing.source_offsets import create_evidence

# Canonical taxonomy mapping: normalized_name -> (category, canonical_name, aliases, regex_pattern)
TAXONOMY: dict[str, tuple[SkillCategory, str, list[str], re.Pattern]] = {
    "python": (
        SkillCategory.PROGRAMMING_LANGUAGE,
        "Python",
        ["py"],
        re.compile(r"\b(?:python(?:\s*3)?|py)\b", re.IGNORECASE),
    ),
    "javascript": (
        SkillCategory.PROGRAMMING_LANGUAGE,
        "JavaScript",
        ["js", "es6", "ecmascript"],
        re.compile(r"\b(?:javascript|js|es6)\b", re.IGNORECASE),
    ),
    "typescript": (
        SkillCategory.PROGRAMMING_LANGUAGE,
        "TypeScript",
        ["ts"],
        re.compile(r"\b(?:typescript|ts)\b", re.IGNORECASE),
    ),
    "go": (
        SkillCategory.PROGRAMMING_LANGUAGE,
        "Go",
        ["golang"],
        re.compile(r"\b(?:golang|go\s+programming)\b|\bgo\b(?=\s*(?:developer|engineer|code|backend|,|\.|\;|\)|and|or))", re.IGNORECASE),
    ),
    "rust": (
        SkillCategory.PROGRAMMING_LANGUAGE,
        "Rust",
        [],
        re.compile(r"\brust\b(?=\s*(?:developer|engineer|programming|code|,|\.))", re.IGNORECASE),
    ),
    "java": (
        SkillCategory.PROGRAMMING_LANGUAGE,
        "Java",
        [],
        re.compile(r"\bjava\b(?!\s*script)", re.IGNORECASE),
    ),
    "cpp": (
        SkillCategory.PROGRAMMING_LANGUAGE,
        "C++",
        ["c plus plus"],
        re.compile(r"\b(?:c\+\+|c\s*plus\s*plus)\b", re.IGNORECASE),
    ),
    "csharp": (
        SkillCategory.PROGRAMMING_LANGUAGE,
        "C#",
        ["c sharp", ".net c#"],
        re.compile(r"\b(?:c#|c\s*sharp)\b", re.IGNORECASE),
    ),
    "sql": (
        SkillCategory.PROGRAMMING_LANGUAGE,
        "SQL",
        ["relational sql"],
        re.compile(r"\bsql\b", re.IGNORECASE),
    ),
    "react": (
        SkillCategory.FRAMEWORK_LIBRARY,
        "React",
        ["reactjs", "react.js"],
        re.compile(r"\b(?:react(?:\.js|js)?)\b", re.IGNORECASE),
    ),
    "nodejs": (
        SkillCategory.FRAMEWORK_LIBRARY,
        "Node.js",
        ["node", "nodejs"],
        re.compile(r"\b(?:node(?:\.js|js)?)\b", re.IGNORECASE),
    ),
    "fastapi": (
        SkillCategory.FRAMEWORK_LIBRARY,
        "FastAPI",
        ["fast api"],
        re.compile(r"\bfast\s*api\b", re.IGNORECASE),
    ),
    "django": (
        SkillCategory.FRAMEWORK_LIBRARY,
        "Django",
        [],
        re.compile(r"\bdjango\b", re.IGNORECASE),
    ),
    "flask": (
        SkillCategory.FRAMEWORK_LIBRARY,
        "Flask",
        [],
        re.compile(r"\bflask\b", re.IGNORECASE),
    ),
    "postgresql": (
        SkillCategory.DATABASE,
        "PostgreSQL",
        ["postgres", "psql"],
        re.compile(r"\b(?:postgresql|postgres|psql)\b", re.IGNORECASE),
    ),
    "mysql": (
        SkillCategory.DATABASE,
        "MySQL",
        [],
        re.compile(r"\bmysql\b", re.IGNORECASE),
    ),
    "mongodb": (
        SkillCategory.DATABASE,
        "MongoDB",
        ["mongo"],
        re.compile(r"\b(?:mongodb|mongo)\b", re.IGNORECASE),
    ),
    "redis": (
        SkillCategory.DATABASE,
        "Redis",
        [],
        re.compile(r"\bredis\b", re.IGNORECASE),
    ),
    "aws": (
        SkillCategory.CLOUD_DEVOPS,
        "AWS",
        ["amazon web services"],
        re.compile(r"\b(?:aws|amazon\s+web\s+services)\b", re.IGNORECASE),
    ),
    "gcp": (
        SkillCategory.CLOUD_DEVOPS,
        "Google Cloud",
        ["google cloud platform"],
        re.compile(r"\b(?:gcp|google\s+cloud(?:\s+platform)?)\b", re.IGNORECASE),
    ),
    "azure": (
        SkillCategory.CLOUD_DEVOPS,
        "Azure",
        ["microsoft azure"],
        re.compile(r"\b(?:azure|microsoft\s+azure)\b", re.IGNORECASE),
    ),
    "docker": (
        SkillCategory.CLOUD_DEVOPS,
        "Docker",
        ["containerization"],
        re.compile(r"\bdocker\b", re.IGNORECASE),
    ),
    "kubernetes": (
        SkillCategory.CLOUD_DEVOPS,
        "Kubernetes",
        ["k8s"],
        re.compile(r"\b(?:kubernetes|k8s)\b", re.IGNORECASE),
    ),
    "terraform": (
        SkillCategory.CLOUD_DEVOPS,
        "Terraform",
        [],
        re.compile(r"\bterraform\b", re.IGNORECASE),
    ),
    "cicd": (
        SkillCategory.CLOUD_DEVOPS,
        "CI/CD",
        ["continuous integration", "github actions"],
        re.compile(r"\b(?:ci[/-]cd|continuous\s+integration|github\s+actions)\b", re.IGNORECASE),
    ),
    "machine_learning": (
        SkillCategory.AI_ML,
        "Machine Learning",
        ["ml", "deep learning"],
        re.compile(r"\b(?:machine\s+learning|deep\s+learning)\b|\bml\b(?=\s*(?:model|pipeline|engineer))", re.IGNORECASE),
    ),
    "pytorch": (
        SkillCategory.AI_ML,
        "PyTorch",
        [],
        re.compile(r"\bpytorch\b", re.IGNORECASE),
    ),
    "tensorflow": (
        SkillCategory.AI_ML,
        "TensorFlow",
        ["tf"],
        re.compile(r"\btensorflow\b", re.IGNORECASE),
    ),
    "rest_api": (
        SkillCategory.TOOLS_PLATFORMS,
        "REST APIs",
        ["restful apis"],
        re.compile(r"\b(?:rest(?:ful)?\s*apis?)\b", re.IGNORECASE),
    ),
    "graphql": (
        SkillCategory.TOOLS_PLATFORMS,
        "GraphQL",
        [],
        re.compile(r"\bgraphql\b", re.IGNORECASE),
    ),
    "agile": (
        SkillCategory.METHODOLOGY,
        "Agile",
        ["scrum"],
        re.compile(r"\b(?:agile|scrum)\b", re.IGNORECASE),
    ),
}

# Regex to detect years of experience associated with a skill
SKILL_YEARS_REGEX = re.compile(
    r"(\d+(?:\.\d+)?)\s*(?:\+|-\s*\d+)?\s*(?:years?|yrs?)(?:\s+of)?(?:\s+experience\s+(?:with|in))?\s+([^,\.\;\n]+)",
    re.IGNORECASE,
)


def extract_skills_from_sections(
    sections: list[JobSection],
    full_source_text: str,
) -> tuple[list[StructuredSkill], list[AtomicRequirement]]:
    """Extract and normalize technical skills across segmented sections."""
    structured_skills: list[StructuredSkill] = []
    atomic_requirements: list[AtomicRequirement] = []
    seen_skills: set[str] = set()

    # Sort sections by priority so MANDATORY and PREFERRED take precedence over RESPONSIBILITIES
    section_priority = {
        "MINIMUM_QUALIFICATIONS": 1,
        "PREFERRED_QUALIFICATIONS": 2,
        "RESPONSIBILITIES": 3,
        "ABOUT_ROLE": 4,
        "GENERAL": 5,
    }
    sorted_sections = sorted(sections, key=lambda s: section_priority.get(s.name, 10))

    for sec in sorted_sections:
        # Determine base category by section
        if sec.name == "MINIMUM_QUALIFICATIONS":
            default_category = RequirementCategory.MANDATORY
        elif sec.name == "PREFERRED_QUALIFICATIONS":
            default_category = RequirementCategory.PREFERRED
        elif sec.name == "RESPONSIBILITIES":
            default_category = RequirementCategory.INFORMATIONAL
        else:
            default_category = RequirementCategory.OPTIONAL

        for line in sec.lines:
            line_str = line.strip()
            if not line_str:
                continue

            for key, (category, canonical_name, aliases, pattern) in TAXONOMY.items():
                if pattern.search(line_str):
                    # Check if negated in this line
                    negated = is_skill_negated(line_str, canonical_name)
                    if negated:
                        # Scoped negation: employer explicitly states this skill is not required
                        continue

                    # Extract years of experience if mentioned
                    min_years = None
                    y_match = re.search(
                        rf"(\d+)(?:\+|-(\d+))?\s*(?:years?|yrs?)[^\.\,\;]*?\b{re.escape(canonical_name)}\b",
                        line_str,
                        re.IGNORECASE,
                    )
                    if not y_match:
                        y_match = re.search(
                            rf"\b{re.escape(canonical_name)}\b[^\.\,\;]*?(\d+)(?:\+|-(\d+))?\s*(?:years?|yrs?)",
                            line_str,
                            re.IGNORECASE,
                        )
                    if y_match:
                        try:
                            min_years = float(y_match.group(1))
                        except Exception:
                            min_years = None

                    # Deduplicate or upgrade category if seen in mandatory section
                    is_mandatory = default_category == RequirementCategory.MANDATORY
                    evidence = create_evidence(
                        supporting_text=line_str,
                        full_source_text=full_source_text,
                        section_name=sec.name,
                        extraction_method=ExtractionMethod.DETERMINISTIC_RULES,
                    )

                    if key not in seen_skills:
                        seen_skills.add(key)
                        structured_skills.append(
                            StructuredSkill(
                                name=canonical_name,
                                normalized_name=key,
                                category=category,
                                min_years=min_years,
                                is_mandatory=is_mandatory,
                                evidence=evidence,
                            )
                        )

                        atomic_req = AtomicRequirement(
                            category=default_category,
                            qualification_type=QualificationType.TECHNICAL_SKILL,
                            name=canonical_name,
                            normalized_value=key,
                            raw_text=line_str,
                            min_years=min_years,
                            is_negated=False,
                            confidence=EvidenceConfidence.EXPLICIT_VERIFIED_SOURCE
                            if evidence.verified_in_source
                            else EvidenceConfidence.STRONGLY_SUPPORTED,
                            confidence_score=1.0 if evidence.verified_in_source else 0.8,
                            evidence=[evidence],
                        )
                        evidence.requirement_id = atomic_req.id
                        atomic_requirements.append(atomic_req)

    return structured_skills, atomic_requirements
