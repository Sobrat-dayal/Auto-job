"""Alert grouping and cooldown manager to avoid notification spam."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
import hashlib
from typing import Optional


class AlertCooldownTracker:
    def __init__(self) -> None:
        self._sent_fingerprints: dict[str, datetime] = {}

    def get_fingerprint(
        self,
        owner_id: str,
        alert_type: str,
        canonical_job_id: Optional[str] = None,
        source_id: Optional[str] = None,
    ) -> str:
        raw = f"{owner_id}:{alert_type}:{canonical_job_id or ''}:{source_id or ''}"
        return hashlib.sha256(raw.encode("utf-8")).hexdigest()

    def should_suppress(
        self,
        fingerprint: str,
        cooldown_minutes: int = 60,
        now: Optional[datetime] = None,
    ) -> bool:
        """Returns True if the identical alert was already generated within the cooldown window."""
        current = now or datetime.now(UTC)
        last_sent = self._sent_fingerprints.get(fingerprint)
        if not last_sent:
            return False

        if current - last_sent < timedelta(minutes=cooldown_minutes):
            return True

        return False

    def record_alert(self, fingerprint: str, now: Optional[datetime] = None) -> None:
        self._sent_fingerprints[fingerprint] = now or datetime.now(UTC)

    def clear(self) -> None:
        self._sent_fingerprints.clear()


cooldown_tracker = AlertCooldownTracker()
