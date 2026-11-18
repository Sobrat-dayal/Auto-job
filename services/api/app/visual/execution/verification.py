"""Visual action verification engine.

Measures visual frame differences and OCR assertions to verify that an input
action produced the expected visual state change on the Windows desktop.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Optional

from ..contracts import (
    CapturedFrame,
    VerificationStatus,
    VisualActionRequest,
)
from ..capture.preprocessing import FramePreprocessor
from ..capture.sessions import CaptureSessionManager
from ..grounding.ocr import WindowsMediaOCREngine

logger = logging.getLogger(__name__)


class VisualActionVerifier:
    """Verifies that visual input actions produced expected state changes."""

    def __init__(
        self,
        session_manager: CaptureSessionManager,
        ocr_engine: Optional[WindowsMediaOCREngine] = None,
        min_diff_threshold: float = 0.0005,  # 0.05% visual change threshold
    ) -> None:
        self.session_manager = session_manager
        self.ocr_engine = ocr_engine or WindowsMediaOCREngine()
        self.min_diff_threshold = min_diff_threshold

    async def verify_action(
        self,
        session_id: str,
        action: VisualActionRequest,
        before_frame: Optional[CapturedFrame],
        post_delay_seconds: float = 0.25,
    ) -> tuple[VerificationStatus, float, Optional[str], Optional[CapturedFrame]]:
        """Captures a post-action frame and evaluates visual state change.

        Returns:
            (VerificationStatus, diff_percentage, explanation, after_frame)
        """
        # If verification is not requested or no before_frame, return skipped
        if not action.wait_for_render and not action.expected_change:
            # Still capture a verification frame if possible
            try:
                after_frame = await self.session_manager.capture_frame(session_id)
                return VerificationStatus.SKIPPED, 0.0, "Verification skipped by request", after_frame
            except Exception:
                return VerificationStatus.SKIPPED, 0.0, "Verification skipped by request", None

        # Wait for target UI rendering
        if post_delay_seconds > 0:
            await asyncio.sleep(post_delay_seconds)

        try:
            after_frame = await self.session_manager.capture_frame(session_id)
        except Exception as e:
            logger.warning(f"Failed to capture post-action verification frame: {e}")
            return VerificationStatus.UNCERTAIN, 0.0, f"Failed to capture post-action frame: {e}", None

        if before_frame is None:
            return VerificationStatus.UNCERTAIN, 0.0, "No pre-action frame available for baseline comparison", after_frame

        # Compute pixel difference
        diff_ratio = FramePreprocessor.compute_frame_difference(before_frame.image, after_frame.image)
        has_visual_change = diff_ratio >= self.min_diff_threshold

        # If an expected text or change was specified, check it
        if action.expected_change:
            expected_lower = action.expected_change.lower().strip()
            # Run OCR on the after_frame
            ocr_res = await self.ocr_engine.recognize_frame(after_frame)
            found = any(expected_lower in line.text.lower() for line in ocr_res.lines)
            if found:
                return (
                    VerificationStatus.VERIFIED,
                    diff_ratio,
                    f"Visual verification succeeded: Expected text '{action.expected_change}' verified in target area (diff={diff_ratio:.4f})",
                    after_frame,
                )
            else:
                if has_visual_change:
                    return (
                        VerificationStatus.UNCERTAIN,
                        diff_ratio,
                        f"Visual change detected (diff={diff_ratio:.4f}), but expected text '{action.expected_change}' was not confirmed by OCR",
                        after_frame,
                    )
                else:
                    return (
                        VerificationStatus.FAILED,
                        diff_ratio,
                        f"Visual verification failed: Expected text '{action.expected_change}' not found and no visual change detected (diff={diff_ratio:.4f})",
                        after_frame,
                    )

        # For generic actions without specific expected_change assertion:
        # A click or keypress usually causes at least a small visual difference (focus ring, cursor, highlight, render)
        if has_visual_change:
            return (
                VerificationStatus.VERIFIED,
                diff_ratio,
                f"Visual change confirmed: {diff_ratio * 100:.3f}% pixel difference detected post-action",
                after_frame,
            )
        else:
            # Some actions (e.g. clicking an already active button or focusing an identical window) may produce 0 diff
            return (
                VerificationStatus.UNCERTAIN,
                diff_ratio,
                f"Minimal or no visual change detected ({diff_ratio * 100:.4f}% diff). Action executed without obvious UI state delta",
                after_frame,
            )
