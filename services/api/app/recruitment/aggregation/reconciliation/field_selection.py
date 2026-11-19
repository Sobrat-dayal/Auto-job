"""Field Selection & Multi-Source Reconciliation (Stage 27)."""

from typing import Any, Optional
from app.recruitment.aggregation.reconciliation.source_authority import get_source_authority_score


def select_best_field_value(
    candidates: list[dict[str, Any]],
    field_name: str,
) -> tuple[Optional[str], Optional[dict[str, Any]]]:
    """Select the most authoritative and complete value for a canonical field.

    Each candidate has:
      'value': str,
      'provider': str,
      'retrieved_at': str,
      'is_verified': bool
    """
    if not candidates:
        return None, None

    # Filter out empty values
    valid_candidates = [c for c in candidates if c.get("value") and str(c.get("value")).strip()]
    if not valid_candidates:
        return None, None

    # Score each candidate by source authority + completeness
    scored = []
    for cand in valid_candidates:
        val = str(cand.get("value")).strip()
        auth = get_source_authority_score(cand.get("provider", ""))
        # Slight bonus for longer/more informative values in titles and descriptions
        completeness = min(1.0, len(val) / 50.0) if field_name in {"title", "display_title", "description"} else 1.0
        score = (auth * 0.7) + (completeness * 0.3)
        scored.append((score, val, cand))

    scored.sort(key=lambda x: x[0], reverse=True)
    best = scored[0]
    return best[1], best[2]
