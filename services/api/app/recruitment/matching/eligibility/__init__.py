"""Eligibility evaluation package for Stage 29 Matching Engine."""

from app.recruitment.matching.eligibility.decisions import determine_matching_outcome
from app.recruitment.matching.eligibility.logical_groups import evaluate_logical_groups

__all__ = [
    "evaluate_logical_groups",
    "determine_matching_outcome",
]
