"""Desktop input ownership and concurrency lease manager (Stage 18)."""

import asyncio
from datetime import UTC, datetime
import logging
from uuid import uuid4

logger = logging.getLogger("autonom.visual.input.ownership")


class InputOwnershipManager:
    """Manages exclusive input lease to prevent competing agents or rapid user conflict."""

    def __init__(self, lease_timeout_seconds: float = 10.0) -> None:
        self.lease_timeout_seconds = lease_timeout_seconds
        self._current_owner: str | None = None
        self._current_token: str | None = None
        self._lease_acquired_at: datetime | None = None
        self._lease_duration: float = lease_timeout_seconds

    def acquire_lease(self, owner_id: str, duration_seconds: float = 10.0) -> str | None:
        """Acquires exclusive input lease for the calling agent or task."""
        now = datetime.now(UTC)
        if self._current_owner and self._lease_acquired_at:
            age = (now - self._lease_acquired_at).total_seconds()
            if age > self._lease_duration:
                logger.warning(f"Input lease for '{self._current_owner}' expired after {age:.1f}s; pre-empting.")
                self._current_owner = None
                self._current_token = None

        if self._current_owner is None or self._current_owner == owner_id:
            self._current_owner = owner_id
            self._current_token = f"lease_{owner_id}_{uuid4().hex[:8]}"
            self._lease_acquired_at = now
            self._lease_duration = duration_seconds
            return self._current_token
        return None

    def release_lease(self, token_or_owner: str) -> bool:
        """Releases the input lease cleanly."""
        if token_or_owner in (self._current_token, self._current_owner):
            self._current_owner = None
            self._current_token = None
            self._lease_acquired_at = None
            return True
        return False

    def is_lease_active(self, token_or_owner: str) -> bool:
        """Checks if specified token or owner holds the active valid lease."""
        if not self._current_token or not self._lease_acquired_at:
            return False
        now = datetime.now(UTC)
        if (now - self._lease_acquired_at).total_seconds() > self._lease_duration:
            return False
        return token_or_owner in (self._current_token, self._current_owner)

    def get_current_owner(self) -> str | None:
        return self._current_owner


input_ownership_manager = InputOwnershipManager()

