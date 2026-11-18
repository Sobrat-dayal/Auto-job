"""Verification Coordinator evaluating post-action state across methods."""

from __future__ import annotations

import logging
from typing import Optional

from app.hybrid.adapters.base import BaseInteractionAdapter
from app.hybrid.contracts import (
    HybridVerificationStatus,
    InteractionAction,
    InteractionResult,
)

logger = logging.getLogger("autonom.hybrid.execution.verification")


class HybridVerificationCoordinator:
    """Evaluates whether an action successfully mutated target state across DOM, UIA, or visual signals."""

    @staticmethod
    async def verify_action(
        adapter: BaseInteractionAdapter,
        action: InteractionAction,
        result: InteractionResult,
    ) -> HybridVerificationStatus:
        """Run post-action verification using the executing adapter."""
        if not result.success:
            return HybridVerificationStatus.FAILED

        try:
            status = await adapter.verify(action, result)
            return status
        except Exception as exc:
            logger.warning("Post-action verification threw exception: %s", exc)
            return HybridVerificationStatus.UNKNOWN_OUTCOME
