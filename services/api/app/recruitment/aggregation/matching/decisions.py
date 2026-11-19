"""Duplicate Decision Evaluator & Policy Manager (Stage 27)."""

from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    JobDuplicateCandidateModel,
    JobDuplicateDecisionModel,
    JobDuplicateReviewRequestModel,
)
from app.recruitment.aggregation.contracts import (
    DuplicateAction,
    DuplicateAssessment,
    DuplicateDecisionState,
)


class DuplicateDecisionManager:
    """Manages recording and evaluating duplicate decisions."""

    async def record_candidate(
        self,
        session: AsyncSession,
        assessment: DuplicateAssessment,
    ) -> JobDuplicateCandidateModel:
        """Persist duplicate candidate record and review request if required."""
        cand = JobDuplicateCandidateModel(
            left_job_id=assessment.left_job_id,
            right_job_id=assessment.right_job_id,
            status=assessment.proposed_status.value,
            similarity_score=assessment.similarity_score,
            matching_factors_json={"positive": assessment.positive_evidence},
            contradictions_json={"negative": assessment.negative_evidence},
            recommended_action=assessment.recommended_action.value,
        )
        session.add(cand)
        await session.flush()

        if assessment.review_required:
            rev = JobDuplicateReviewRequestModel(
                candidate_id=cand.id,
                priority="high" if assessment.similarity_score >= 0.85 else "medium",
                status="pending",
                reason=assessment.explanation,
            )
            session.add(rev)
            await session.flush()

        return cand


duplicate_decision_manager = DuplicateDecisionManager()
