"""Source Observation Freshness and Timestamp Tracking (Stage 27)."""

from datetime import UTC, datetime
from typing import Optional


def parse_timestamp_safe(ts_str: Optional[str]) -> Optional[datetime]:
    """Parse ISO timestamp safely with UTC fallback."""
    if not ts_str:
        return None
    try:
        clean = ts_str.replace("Z", "+00:00")
        return datetime.fromisoformat(clean)
    except Exception:
        return None


def calculate_freshness_metrics(
    posted_at: Optional[str],
    updated_at: Optional[str],
    discovered_at: Optional[str],
    last_fetched_at: Optional[str],
) -> dict[str, Optional[str]]:
    """Compute normalized timeline metrics without overwriting original dates."""
    return {
        "original_publication_date": posted_at,
        "provider_update_date": updated_at,
        "first_discovered_date": discovered_at or datetime.now(UTC).isoformat(),
        "last_verified_active_date": last_fetched_at or datetime.now(UTC).isoformat(),
    }
