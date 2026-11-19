"""Duplicate Review Queue & Human Decision Handling (Stage 27)."""

from datetime import UTC, datetime
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import (
    CanonicalJobModel,
    CanonicalJobRelationshipModel,
    JobDuplicateCandidateModel,
    JobDuplicateDecisionModel,
    JobDuplicateReviewRequestModel,
)
from app.recruitment.aggregation.contracts import (
    DuplicateAction,
    DuplicateCandidateRecord,
    DuplicateDecisionState,
)
from app.recruitment.aggregation.identity_operations.merge import merge_execution_engine


class DuplicateReviewQueueManager:
    """Manages pending human duplicate review items and resolution decisions."""

    async def list_pending_reviews(
        self,
        session: AsyncSession,
        limit: int = 50,
        offset: int = 0,
    ) -> list[DuplicateCandidateRecord]:
        stmt = (
            select(JobDuplicateCandidateModel)
            .where(JobDuplicateCandidateModel.status.in_(["proposed", "in_review", "possible_duplicate"]))
            .order_by(JobDuplicateCandidateModel.similarity_score.desc())
            .limit(limit)
            .offset(offset)
        )
        res = await session.execute(stmt)
        candidates = res.scalars().all()

        records = []
        for c in candidates:
            records.append(
                DuplicateCandidateRecord(
                    id=c.id,
                    left_job_id=c.left_job_id,
                    right_job_id=c.right_job_id,
                    status=DuplicateDecisionState(c.status) if c.status in DuplicateDecisionState._value2member_map_ else DuplicateDecisionState.POSSIBLE_DUPLICATE,
                    similarity_score=c.similarity_score,
                    matching_factors=c.matching_factors_json or {},
                    contradictions=c.contradictions_json or {},
                    recommended_action=DuplicateAction(c.recommended_action) if c.recommended_action in DuplicateAction._value2member_map_ else DuplicateAction.DEFER,
                    created_at=c.created_at.isoformat() if hasattr(c.created_at, "isoformat") else str(c.created_at),
                )
            )
        return records

    async def submit_review_decision(
        self,
        session: AsyncSession,
        candidate_id: str,
        decision: DuplicateAction,
        reason: str = "User reviewed decision",
        decided_by: str = "user_manual",
    ) -> bool:
        stmt = select(JobDuplicateCandidateModel).where(JobDuplicateCandidateModel.id == candidate_id)
        res = await session.execute(stmt)
        cand = res.scalar_one_or_none()
        if not cand:
            return False

        # Record decision audit
        dec_model = JobDuplicateDecisionModel(
            candidate_id=cand.id,
            left_job_id=cand.left_job_id,
            right_job_id=cand.right_job_id,
            decision=decision.value,
            decided_by=decided_by,
            reason=reason,
            decided_at=datetime.now(UTC),
        )
        session.add(dec_model)

        if decision == DuplicateAction.MERGE:
            cand.status = DuplicateDecisionState.CONFIRMED_DUPLICATE.value
            # Execute actual merge: left absorbs right
            await merge_execution_engine.execute_merge(
                session=session,
                surviving_job_id=cand.left_job_id,
                superseded_job_id=cand.right_job_id,
                actor=decided_by,
                reason=reason,
            )
        elif decision == DuplicateAction.KEEP_SEPARATE:
            cand.status = DuplicateDecisionState.CONFIRMED_DISTINCT.value
        elif decision == DuplicateAction.MARK_RELATED:
            cand.status = DuplicateDecisionState.RELATED_BUT_DISTINCT.value
            rel = CanonicalJobRelationshipModel(
                canonical_job_id=cand.left_job_id,
                related_job_id=cand.right_job_id,
                relationship_type="similar_role",
                confidence=cand.similarity_score,
                notes=reason,
                created_at=datetime.now(UTC),
            )
            session.add(rel)
        elif decision == DuplicateAction.DEFER:
            cand.status = DuplicateDecisionState.POSSIBLE_DUPLICATE.value

        # Update review request status if present
        stmt_rev = select(JobDuplicateReviewRequestModel).where(
            JobDuplicateReviewRequestModel.candidate_id == candidate_id
        )
        res_rev = await session.execute(stmt_rev)
        rev = res_rev.scalar_one_or_none()
        if rev:
            rev.status = "approved" if decision == DuplicateAction.MERGE else "rejected"

        await session.flush()
        return True


duplicate_review_queue_manager = DuplicateReviewQueueManager()
