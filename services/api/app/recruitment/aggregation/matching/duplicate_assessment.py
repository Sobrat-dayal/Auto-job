"""Duplicate Assessment Synthesizer (Stage 27)."""

from typing import Any
from app.db.models import CanonicalJobModel
from app.recruitment.aggregation.contracts import (
    DuplicateAction,
    DuplicateAssessment,
    DuplicateDecisionState,
)
from app.recruitment.aggregation.matching.deterministic_rules import evaluate_deterministic_match
from app.recruitment.aggregation.matching.negative_evidence import evaluate_negative_evidence
from app.recruitment.aggregation.matching.similarity import calculate_job_similarity


def assess_duplicate_candidate(
    job_a: CanonicalJobModel,
    job_b: CanonicalJobModel,
    min_similarity_threshold: float = 0.75,
    auto_merge_threshold: float = 0.92,
) -> DuplicateAssessment:
    """Evaluate duplicate probability between two canonical jobs with explainable evidence."""

    # 1. Check Negative Evidence First (False Merge Prevention)
    has_fatal_contradiction, negative_signals = evaluate_negative_evidence(job_a, job_b)
    if has_fatal_contradiction:
        return DuplicateAssessment(
            left_job_id=job_a.id,
            right_job_id=job_b.id,
            proposed_status=DuplicateDecisionState.CONFIRMED_DISTINCT,
            similarity_score=0.0,
            positive_evidence=[],
            negative_evidence=negative_signals,
            missing_evidence=[],
            rule_version="1.0.0",
            review_required=False,
            recommended_action=DuplicateAction.KEEP_SEPARATE,
            explanation=f"Distinct vacancies: {negative_signals[0]['message']}",
        )

    # 2. Check Deterministic Rules
    is_exact, exact_conf, positive_signals = evaluate_deterministic_match(job_a, job_b)
    if is_exact:
        return DuplicateAssessment(
            left_job_id=job_a.id,
            right_job_id=job_b.id,
            proposed_status=DuplicateDecisionState.CONFIRMED_DUPLICATE,
            similarity_score=exact_conf,
            positive_evidence=positive_signals,
            negative_evidence=[],
            missing_evidence=[],
            rule_version="1.0.0",
            review_required=False,
            recommended_action=DuplicateAction.MERGE,
            explanation="Exact match confirmed by deterministic rule",
        )

    # 3. Calculate Multi-Factor Similarity
    similarity_score, factor_breakdown = calculate_job_similarity(job_a, job_b)
    positive_signals.append({
        "rule": "composite_similarity",
        "weight": similarity_score,
        "factors": factor_breakdown,
    })

    if similarity_score >= auto_merge_threshold:
        # High similarity candidate
        return DuplicateAssessment(
            left_job_id=job_a.id,
            right_job_id=job_b.id,
            proposed_status=DuplicateDecisionState.STRONG_DUPLICATE_CANDIDATE,
            similarity_score=similarity_score,
            positive_evidence=positive_signals,
            negative_evidence=negative_signals,
            missing_evidence=[],
            rule_version="1.0.0",
            review_required=True,  # Queue for human review if not 100% deterministic
            recommended_action=DuplicateAction.MERGE,
            explanation=f"Strong duplicate candidate with score {similarity_score:.2f}",
        )
    elif similarity_score >= min_similarity_threshold:
        return DuplicateAssessment(
            left_job_id=job_a.id,
            right_job_id=job_b.id,
            proposed_status=DuplicateDecisionState.POSSIBLE_DUPLICATE,
            similarity_score=similarity_score,
            positive_evidence=positive_signals,
            negative_evidence=negative_signals,
            missing_evidence=["verified_requisition_id"],
            rule_version="1.0.0",
            review_required=True,
            recommended_action=DuplicateAction.DEFER,
            explanation=f"Possible duplicate candidate with score {similarity_score:.2f}, requires review",
        )
    else:
        return DuplicateAssessment(
            left_job_id=job_a.id,
            right_job_id=job_b.id,
            proposed_status=DuplicateDecisionState.CONFIRMED_DISTINCT,
            similarity_score=similarity_score,
            positive_evidence=positive_signals,
            negative_evidence=[],
            missing_evidence=[],
            rule_version="1.0.0",
            review_required=False,
            recommended_action=DuplicateAction.KEEP_SEPARATE,
            explanation=f"Distinct vacancies with low similarity score {similarity_score:.2f}",
        )
