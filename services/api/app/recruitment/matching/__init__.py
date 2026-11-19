"""Applicant-to-Job Matching and Prioritization package for AUTONOM (Stage 29)."""

from app.recruitment.matching.contracts import (
    ApplicationReadiness,
    JobComparisonMatrix,
    JobMatchEvaluation,
    MatchingOutcome,
    RankedOpportunityItem,
    RankingOverview,
    RequirementEvaluationResult,
    RequirementMatchCategory,
    RubricConfig,
    SimulationRequest,
    SimulationResponse,
    SkillGapItem,
)
from app.recruitment.matching.service import (
    JobMatchingService,
    job_matching_service,
)

__all__ = [
    "job_matching_service",
    "JobMatchingService",
    "JobMatchEvaluation",
    "MatchingOutcome",
    "RequirementMatchCategory",
    "ApplicationReadiness",
    "SkillGapItem",
    "RubricConfig",
    "RankedOpportunityItem",
    "RankingOverview",
    "JobComparisonMatrix",
    "SimulationRequest",
    "SimulationResponse",
    "RequirementEvaluationResult",
]
