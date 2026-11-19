"""Human review queue and manual correction management."""

from datetime import UTC, datetime

from app.recruitment.intelligence.contracts import ReviewQueueItem, ReviewStatus


def resolve_review_item(
    item: ReviewQueueItem,
    decision: ReviewStatus,
    reviewer: str = "human_operator",
    notes: str | None = None,
) -> ReviewQueueItem:
    """Apply an authorized manual decision to a pending review queue item."""
    item.status = decision
    item.reviewer_decision = decision.value
    item.reviewer_notes = notes
    return item
