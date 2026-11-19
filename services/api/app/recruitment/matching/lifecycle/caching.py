"""Deterministic cache management for Stage 29 Matching Engine."""

from __future__ import annotations

import hashlib
import logging
from app.recruitment.matching.contracts import (
    ApplicantSnapshotData,
    CareerStrategySnapshotData,
    JobIntelligenceSnapshotData,
    JobMatchEvaluation,
    RubricConfig,
)

logger = logging.getLogger("autonom.recruitment.matching.lifecycle.caching")

# In-memory evaluation cache keyed by immutable input hash
_EVALUATION_CACHE: dict[str, JobMatchEvaluation] = {}


def generate_cache_key(
    applicant_snapshot: ApplicantSnapshotData,
    job_intelligence: JobIntelligenceSnapshotData,
    career_strategy: CareerStrategySnapshotData,
    rubric: RubricConfig,
) -> str:
    """Builds a deterministic SHA-256 cache key from immutable input versions (Section 99)."""
    raw_key = (
        f"{applicant_snapshot.profile_id}:v{applicant_snapshot.version}:"
        f"{job_intelligence.canonical_job_id}:v{job_intelligence.canonical_job_version}:"
        f"{career_strategy.strategy_id}:"
        f"{rubric.id}:v{rubric.version}"
    )
    return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()


def get_cached_evaluation(cache_key: str) -> JobMatchEvaluation | None:
    """Retrieves an existing evaluation from the cache if present."""
    return _EVALUATION_CACHE.get(cache_key)


def set_cached_evaluation(cache_key: str, evaluation: JobMatchEvaluation) -> None:
    """Stores an evaluation result in the cache."""
    _EVALUATION_CACHE[cache_key] = evaluation


def clear_cache() -> None:
    """Flushes the in-memory matching cache."""
    _EVALUATION_CACHE.clear()
