"""Unified Foreground Input Ownership and Lease Management for the Hybrid Engine."""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

logger = logging.getLogger("autonom.hybrid.execution.input_ownership")


class HybridInputOwnershipCoordinator:
    """Ensures exclusive ownership of mouse and keyboard input across Stage 17 and Stage 18 execution."""

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._current_owner: Optional[str] = None

    @property
    def current_owner(self) -> Optional[str]:
        return self._current_owner

    async def acquire_lease(self, owner_id: str, timeout_seconds: float = 5.0) -> bool:
        """Acquire exclusive input lease for a task or action."""
        try:
            await asyncio.wait_for(self._lock.acquire(), timeout=timeout_seconds)
            self._current_owner = owner_id
            logger.debug("Input lease acquired by: %s", owner_id)
            return True
        except asyncio.TimeoutError:
            logger.warning("Input lease acquisition timed out for %s (current owner: %s)", owner_id, self._current_owner)
            return False

    def release_lease(self, owner_id: str) -> None:
        """Release the active input lease if held by the owner."""
        if self._current_owner == owner_id:
            self._current_owner = None
            if self._lock.locked():
                self._lock.release()
            logger.debug("Input lease released by: %s", owner_id)


# Global singleton instance
_input_coordinator: Optional[HybridInputOwnershipCoordinator] = None


def get_input_coordinator() -> HybridInputOwnershipCoordinator:
    """Return shared HybridInputOwnershipCoordinator singleton."""
    global _input_coordinator
    if _input_coordinator is None:
        _input_coordinator = HybridInputOwnershipCoordinator()
    return _input_coordinator
