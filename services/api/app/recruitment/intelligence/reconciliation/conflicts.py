"""Multi-source conflict detection and reconciliation."""

from app.recruitment.intelligence.contracts import (
    ConflictRecord,
    ConflictType,
    JobIntelligenceRecord,
    ResolutionStrategy,
    ReviewQueueItem,
    ReviewStatus,
)


def detect_multi_source_conflicts(
    record_a: JobIntelligenceRecord,
    record_b: JobIntelligenceRecord,
    source_a_id: str = "source_a",
    source_b_id: str = "source_b",
) -> tuple[list[ConflictRecord], list[ReviewQueueItem]]:
    """Detect substantive contradictions between two sources for the same canonical vacancy."""
    conflicts: list[ConflictRecord] = []
    reviews: list[ReviewQueueItem] = []

    # 1. Work arrangement conflict (e.g. Remote vs Hybrid/Onsite)
    wa_a = record_a.employment_conditions.workplace_type
    wa_b = record_b.employment_conditions.workplace_type
    if wa_a != wa_b and wa_a.value != "UNKNOWN" and wa_b.value != "UNKNOWN":
        c = ConflictRecord(
            conflict_type=ConflictType.WORK_ARRANGEMENT,
            source_a_id=source_a_id,
            source_a_text=f"Workplace: {wa_a.value}",
            source_b_id=source_b_id,
            source_b_text=f"Workplace: {wa_b.value}",
            resolution_strategy=ResolutionStrategy.PENDING,
        )
        conflicts.append(c)
        reviews.append(
            ReviewQueueItem(
                intelligence_id=record_a.id,
                conflict_id=c.id,
                review_type="CONFLICTING_WORK_ARRANGEMENT",
                reason=f"Source conflict on workplace type: '{wa_a.value}' vs '{wa_b.value}'",
                status=ReviewStatus.PENDING,
            )
        )

    # 2. Salary range conflict
    sal_a = record_a.compensation
    sal_b = record_b.compensation
    if sal_a.is_disclosed and sal_b.is_disclosed:
        if (sal_a.base_min != sal_b.base_min or sal_a.base_max != sal_b.base_max) and sal_a.currency == sal_b.currency:
            c = ConflictRecord(
                conflict_type=ConflictType.SALARY_RANGE,
                source_a_id=source_a_id,
                source_a_text=f"{sal_a.currency} {sal_a.base_min} - {sal_a.base_max}",
                source_b_id=source_b_id,
                source_b_text=f"{sal_b.currency} {sal_b.base_min} - {sal_b.base_max}",
                resolution_strategy=ResolutionStrategy.PENDING,
            )
            conflicts.append(c)
            reviews.append(
                ReviewQueueItem(
                    intelligence_id=record_a.id,
                    conflict_id=c.id,
                    review_type="CONFLICTING_SALARY_RANGE",
                    reason=f"Source conflict on compensation: '{sal_a.base_min}-{sal_a.base_max}' vs '{sal_b.base_min}-{sal_b.base_max}'",
                    status=ReviewStatus.PENDING,
                )
            )

    # 3. Visa sponsorship conflict
    sp_a = record_a.eligibility.visa_sponsorship_offered
    sp_b = record_b.eligibility.visa_sponsorship_offered
    if sp_a is not None and sp_b is not None and sp_a != sp_b:
        c = ConflictRecord(
            conflict_type=ConflictType.VISA_SPONSORSHIP,
            source_a_id=source_a_id,
            source_a_text=f"Sponsorship offered: {sp_a}",
            source_b_id=source_b_id,
            source_b_text=f"Sponsorship offered: {sp_b}",
            resolution_strategy=ResolutionStrategy.PENDING,
        )
        conflicts.append(c)
        reviews.append(
            ReviewQueueItem(
                intelligence_id=record_a.id,
                conflict_id=c.id,
                review_type="CONFLICTING_VISA_SPONSORSHIP",
                reason="One source states visa sponsorship is offered while another indicates refusal",
                status=ReviewStatus.PENDING,
            )
        )

    return conflicts, reviews
