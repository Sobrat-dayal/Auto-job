"""Opportunity ranking package for Stage 29 Matching Engine."""

from app.recruitment.matching.ranking.prioritization import rank_opportunities
from app.recruitment.matching.ranking.rubric import (
    DEFAULT_RUBRIC,
    get_rubric,
    list_rubrics,
    register_rubric,
)
from app.recruitment.matching.ranking.scoring import compute_relevance_index

__all__ = [
    "DEFAULT_RUBRIC",
    "get_rubric",
    "register_rubric",
    "list_rubrics",
    "compute_relevance_index",
    "rank_opportunities",
]
