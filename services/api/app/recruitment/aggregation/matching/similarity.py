"""Multi-Factor Similarity Scoring Engine (Stage 27)."""

from typing import Any
from app.db.models import CanonicalJobModel
from app.recruitment.aggregation.normalization.descriptions import (
    calculate_ngram_jaccard,
    calculate_token_cosine_similarity,
)


def calculate_job_similarity(
    job_a: CanonicalJobModel,
    job_b: CanonicalJobModel,
) -> tuple[float, dict[str, Any]]:
    """Compute weighted composite similarity between two job postings."""
    factors: dict[str, Any] = {}

    # 1. Title Similarity (character 3-gram Jaccard)
    title_sim = calculate_ngram_jaccard(job_a.display_title, job_b.display_title)
    factors["title_similarity"] = title_sim

    # 2. Description Similarity (token cosine / jaccard)
    desc_a = job_a.description_reference or ""
    desc_b = job_b.description_reference or ""
    if desc_a and desc_b:
        desc_sim = calculate_token_cosine_similarity(desc_a, desc_b)
    else:
        desc_sim = title_sim  # fallback if description missing
    factors["description_similarity"] = desc_sim

    # 3. Location & Workplace Similarity
    loc_a = (job_a.location_summary or "").lower()
    loc_b = (job_b.location_summary or "").lower()
    if loc_a and loc_b:
        loc_sim = calculate_ngram_jaccard(loc_a, loc_b)
    else:
        loc_sim = 0.5
    factors["location_similarity"] = loc_sim

    # 4. Employment Type Similarity
    type_a = (job_a.employment_type or "").lower()
    type_b = (job_b.employment_type or "").lower()
    if type_a and type_b:
        type_sim = 1.0 if type_a == type_b else 0.0
    else:
        type_sim = 0.5
    factors["employment_type_similarity"] = type_sim

    # Composite weighted score: Title 0.40, Desc 0.40, Loc 0.10, Type 0.10
    composite = (
        (title_sim * 0.40)
        + (desc_sim * 0.40)
        + (loc_sim * 0.10)
        + (type_sim * 0.10)
    )
    score = round(min(1.0, max(0.0, composite)), 4)
    factors["composite_score"] = score

    return score, factors
