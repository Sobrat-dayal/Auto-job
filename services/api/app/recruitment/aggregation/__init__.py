"""Job Aggregation and Canonical Deduplication Engine (Stage 27)."""

from app.recruitment.aggregation.contracts import (
    AggregationOverviewStats,
    CanonicalEmployerRecord,
    CanonicalJobRecord,
    DuplicateAssessment,
    DuplicateCandidateRecord,
    MergeExecuteResponse,
    MergePreviewResponse,
    SplitExecuteResponse,
    SplitPreviewResponse,
)
from app.recruitment.aggregation.service import JobAggregationService, job_aggregation_service

__all__ = [
    "JobAggregationService",
    "job_aggregation_service",
    "CanonicalJobRecord",
    "CanonicalEmployerRecord",
    "DuplicateAssessment",
    "DuplicateCandidateRecord",
    "MergePreviewResponse",
    "MergeExecuteResponse",
    "SplitPreviewResponse",
    "SplitExecuteResponse",
    "AggregationOverviewStats",
]
