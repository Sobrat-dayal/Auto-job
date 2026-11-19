"""Configurable ranking rubric and dimension definitions for Stage 29 Matching Engine."""

from __future__ import annotations

import logging
from app.recruitment.matching.contracts import RubricConfig

logger = logging.getLogger("autonom.recruitment.matching.ranking.rubric")

DEFAULT_RUBRIC = RubricConfig(
    id="rubric_default_v1",
    version=1,
    name="Standard AUTONOM Recruitment Rubric",
    description="Balanced scoring across mandatory qualifications, preferred skills, location, and salary.",
    is_default=True,
    weights={
        "qualification_alignment": 0.25,
        "preferred_skills": 0.15,
        "role_family": 0.15,
        "experience_duration": 0.10,
        "work_arrangement": 0.10,
        "compensation": 0.10,
        "employer_preference": 0.05,
        "posting_freshness": 0.10,
    },
    missing_data_policy="conservative",
)

_RUBRIC_REGISTRY: dict[str, RubricConfig] = {
    DEFAULT_RUBRIC.id: DEFAULT_RUBRIC,
}


def get_rubric(rubric_id: str | None = None) -> RubricConfig:
    """Retrieves a ranking rubric by ID, defaulting to the standard rubric."""
    if rubric_id and rubric_id in _RUBRIC_REGISTRY:
        return _RUBRIC_REGISTRY[rubric_id]
    return DEFAULT_RUBRIC


def register_rubric(rubric: RubricConfig) -> None:
    """Registers or updates a custom ranking rubric."""
    _RUBRIC_REGISTRY[rubric.id] = rubric


def list_rubrics() -> list[RubricConfig]:
    """Returns all registered ranking rubrics."""
    return list(_RUBRIC_REGISTRY.values())
