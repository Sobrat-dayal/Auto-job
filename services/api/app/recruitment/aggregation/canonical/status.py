"""Posting Status Reconciliation Engine (Stage 27)."""

from app.recruitment.aggregation.contracts import CanonicalJobStatus


def reconcile_canonical_status(
    source_availabilities: list[dict[str, str]],
    is_partial_snapshot: bool = False,
) -> CanonicalJobStatus:
    """Reconcile canonical posting status across multiple sources conservatively.

    Rules:
    - If at least ONE authoritative source observes the job as 'available', it is ACTIVE.
    - If a snapshot was partial or interrupted, missing postings CANNOT be marked closed!
    - If all authoritative sources mark the job closed/expired, it is CLOSED.
    - If a source was unavailable (HTTP 500 / network error), do not mark closed.
    """
    if not source_availabilities:
        return CanonicalJobStatus.UNKNOWN

    statuses = [s.get("availability", "unknown").lower() for s in source_availabilities]

    # Rule 1: If any source verifies it as available, it is active
    if "available" in statuses:
        return CanonicalJobStatus.ACTIVE

    # Rule 2: If the only signal was a partial snapshot or source failure, keep active or possibly_active
    if is_partial_snapshot or any(s in {"source_unavailable", "rate_limited", "interrupted"} for s in statuses):
        return CanonicalJobStatus.POSSIBLY_ACTIVE

    # Rule 3: If all observed sources explicitly confirm closure
    if all(s in {"closed", "expired", "removed"} for s in statuses):
        return CanonicalJobStatus.CLOSED

    return CanonicalJobStatus.POSSIBLY_ACTIVE
