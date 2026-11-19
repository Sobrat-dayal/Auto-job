"""Lifecycle management for Stage 29 Matching Engine."""

from app.recruitment.matching.lifecycle.caching import (
    clear_cache,
    generate_cache_key,
    get_cached_evaluation,
    set_cached_evaluation,
)
from app.recruitment.matching.lifecycle.invalidation import (
    invalidate_for_job_update,
    invalidate_for_policy_update,
    invalidate_for_profile_update,
)

__all__ = [
    "generate_cache_key",
    "get_cached_evaluation",
    "set_cached_evaluation",
    "clear_cache",
    "invalidate_for_profile_update",
    "invalidate_for_job_update",
    "invalidate_for_policy_update",
]
