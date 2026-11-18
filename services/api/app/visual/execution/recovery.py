"""Visual action recovery manager.

Provides bounded recovery strategies when visual grounding or action verification
fails due to transient UI state changes, dynamic popups, or rendering latencies.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Any, Callable, Coroutine, Optional

from ..contracts import (
    CapturedFrame,
    VerificationStatus,
    VisualActionResult,
    VisualGroundingResult,
)
from ..capture.sessions import CaptureSessionManager
from ..grounding.vision import VisualGroundingService

logger = logging.getLogger(__name__)


class VisualRecoveryManager:
    """Manages recovery attempts when visual interactions fail verification."""

    def __init__(
        self,
        session_manager: CaptureSessionManager,
        grounding_service: VisualGroundingService,
        max_attempts: int = 3,
        backoff_seconds: float = 0.5,
    ) -> None:
        self.session_manager = session_manager
        self.grounding_service = grounding_service
        self.max_attempts = max_attempts
        self.backoff_seconds = backoff_seconds
        self._recovery_history: list[dict[str, Any]] = []

    @property
    def history(self) -> list[dict[str, Any]]:
        return list(self._recovery_history)

    async def attempt_recovery(
        self,
        session_id: str,
        query: str,
        failed_result: VisualActionResult,
        action_fn: Callable[[VisualGroundingResult], Coroutine[Any, Any, VisualActionResult]],
        attempt: int = 1,
    ) -> VisualActionResult:
        """Executes a bounded recovery attempt:

        1. Backoff pause for UI settling
        2. Capture fresh frame
        3. Re-ground query
        4. Re-execute action if grounded
        5. Recurse if still failed and attempts remaining
        """
        if attempt > self.max_attempts:
            logger.warning(f"Recovery failed: Exceeded maximum attempts ({self.max_attempts}) for query '{query}'")
            return failed_result

        delay = self.backoff_seconds * attempt
        logger.info(f"Visual recovery attempt {attempt}/{self.max_attempts} for '{query}' after {delay:.2f}s delay")
        await asyncio.sleep(delay)

        event = {
            "attempt": attempt,
            "session_id": session_id,
            "query": query,
            "previous_status": failed_result.verification_status,
            "success": False,
        }

        try:
            # 1. Capture fresh frame
            fresh_frame = await self.session_manager.capture_frame(session_id)

            # 2. Re-ground
            grounding_res = await self.grounding_service.ground(
                frame=fresh_frame,
                query=query,
                target_type=fresh_frame.metadata.target_type,
                target_hwnd=fresh_frame.metadata.target_hwnd,
                display_index=fresh_frame.metadata.display_index,
            )

            if not grounding_res.success:
                logger.info(f"Recovery attempt {attempt}: Failed to re-ground '{query}'")
                event["error"] = "Re-grounding failed"
                self._recovery_history.append(event)
                # Try next attempt if available
                return await self.attempt_recovery(
                    session_id=session_id,
                    query=query,
                    failed_result=failed_result,
                    action_fn=action_fn,
                    attempt=attempt + 1,
                )

            # 3. Re-execute action
            new_result = await action_fn(grounding_res)
            if new_result.verification_status in (VerificationStatus.VERIFIED, VerificationStatus.SKIPPED):
                logger.info(f"Recovery attempt {attempt} succeeded for '{query}'")
                event["success"] = True
                self._recovery_history.append(event)
                return new_result

            # If still uncertain or failed, recurse
            event["error"] = f"Action still {new_result.verification_status}"
            self._recovery_history.append(event)
            return await self.attempt_recovery(
                session_id=session_id,
                query=query,
                failed_result=new_result,
                action_fn=action_fn,
                attempt=attempt + 1,
            )

        except Exception as e:
            logger.error(f"Error during visual recovery attempt {attempt}: {e}")
            event["error"] = str(e)
            self._recovery_history.append(event)
            return await self.attempt_recovery(
                session_id=session_id,
                query=query,
                failed_result=failed_result,
                action_fn=action_fn,
                attempt=attempt + 1,
            )
