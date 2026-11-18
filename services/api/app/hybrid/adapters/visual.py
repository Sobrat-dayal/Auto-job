"""Visual Grounding and Coordinate Interaction Adapter (Stage 18 Bridge)."""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from app.hybrid.adapters.base import BaseInteractionAdapter
from app.hybrid.contracts import (
    CapabilityProbe,
    HybridActionType,
    HybridVerificationStatus,
    InteractionAction,
    InteractionMethod,
    InteractionObservation,
    InteractionResult,
    InteractionTarget,
    ObservationRequest,
    SurfaceType,
    TargetType,
)
from app.visual.contracts import Point2D, VerificationStatus, VisualActionType
from app.visual.service import (
    VisualActionRequest,
    VisualComputerService,
    visual_computer_service as default_visual_service,
)

logger = logging.getLogger("autonom.hybrid.adapters.visual")


class VisualAdapter(BaseInteractionAdapter):
    """Adapter bridging screenshot capture, WinRT OCR, and SendInput visual control into the Hybrid Engine."""

    def __init__(self, service: Optional[VisualComputerService] = None) -> None:
        super().__init__(method=InteractionMethod.VISUAL_GROUNDING)
        self._service = service or default_visual_service

    @property
    def service(self) -> VisualComputerService:
        return self._service

    async def probe(self, target: InteractionTarget) -> CapabilityProbe:
        """Probe if visual capture, OCR, and coordinate input are applicable."""
        # Visual is universally capable of observing any visible desktop surface,
        # but has a higher resource cost (4/5) and lower default preference when structural methods exist.
        is_custom_or_visual = (
            target.target_type in (
                TargetType.VISUAL_CAPTURE_TARGET,
                TargetType.VISUAL_REGION,
            )
            or target.surface_type == SurfaceType.CUSTOM_RENDERED
            or bool(target.coordinates)
            or bool(target.visual_target_name)
        )

        confidence = 0.90 if is_custom_or_visual else 0.60

        supported_actions = [
            HybridActionType.CLICK.value,
            HybridActionType.DOUBLE_CLICK.value,
            HybridActionType.RIGHT_CLICK.value,
            HybridActionType.ENTER_TEXT.value,
            HybridActionType.SCROLL.value,
            HybridActionType.KEY_PRESS.value,
            HybridActionType.HOTKEY.value,
            HybridActionType.INSPECT.value,
        ]

        return CapabilityProbe(
            method=self.method,
            is_available=True,
            is_applicable=True,
            confidence_score=confidence,
            supported_actions=supported_actions,
            required_permissions=["visual:capture", "visual:input", "visual:ocr"],
            resource_cost_score=4,  # Higher compute & token cost
            latency_ms_estimate=85,
            verification_supported=True,
            reason="Visual capture with WinRT OCR and coordinate input available",
        )

    async def observe(self, request: ObservationRequest) -> InteractionObservation:
        """Capture screenshot and extract visible text via offline WinRT OCR."""
        target = request.target
        target_name = target.visual_target_name or ""

        ocr_summary = ""
        visual_detections: list[dict[str, Any]] = []

        try:
            # Run OCR on the screen
            ocr_result = await self.service.run_ocr()
            ocr_summary = f"Detected {len(ocr_result.lines)} text lines via WinRT OCR"
            visual_detections = [
                {
                    "text": line.text,
                    "confidence": line.confidence,
                    "bounds": {
                        "x_min": line.bounds.x_min,
                        "y_min": line.bounds.y_min,
                        "x_max": line.bounds.x_max,
                        "y_max": line.bounds.y_max,
                    },
                }
                for line in ocr_result.lines[:30]
            ]
        except Exception as exc:
            logger.warning("Visual observation/OCR failed: %s", exc)
            ocr_summary = f"Visual capture notice: {exc}"

        return InteractionObservation(
            target_id=target.target_id,
            method=self.method,
            surface_type=SurfaceType.CUSTOM_RENDERED,
            observed_text=ocr_summary,
            structure_summary=ocr_summary,
            visual_detections=visual_detections,
            is_valid=True,
            is_stale=False,
        )

    async def execute(self, request: InteractionAction) -> InteractionResult:
        """Execute coordinate-based mouse or keyboard input via Windows SendInput."""
        start_time = time.perf_counter()
        target = request.target

        # Map action type
        action_map = {
            HybridActionType.CLICK: VisualActionType.CLICK,
            HybridActionType.DOUBLE_CLICK: VisualActionType.DOUBLE_CLICK,
            HybridActionType.RIGHT_CLICK: VisualActionType.RIGHT_CLICK,
            HybridActionType.ENTER_TEXT: VisualActionType.ENTER_TEXT,
            HybridActionType.KEY_PRESS: VisualActionType.PRESS_KEY,
            HybridActionType.SCROLL: VisualActionType.SCROLL,
        }
        v_type = action_map.get(request.action_type, VisualActionType.CLICK)

        # Determine target point
        target_point: Optional[Point2D] = None
        if target.coordinates and "x" in target.coordinates and "y" in target.coordinates:
            target_point = Point2D(x=int(target.coordinates["x"]), y=int(target.coordinates["y"]))
        elif target.visual_target_name:
            # Attempt OCR ground search for target text
            try:
                g_res = await self.service.find_text(target.visual_target_name)
                if g_res.matches:
                    center = g_res.matches[0].center_point
                    target_point = Point2D(x=center.x, y=center.y)
            except Exception as exc:
                logger.warning("Visual text lookup failed for '%s': %s", target.visual_target_name, exc)

        # Fallback to default safe point if still unset for non-keyboard actions
        if target_point is None and v_type in (
            VisualActionType.CLICK,
            VisualActionType.DOUBLE_CLICK,
            VisualActionType.RIGHT_CLICK,
        ):
            target_point = Point2D(x=500, y=500)

        try:
            v_req = VisualActionRequest(
                action_type=v_type,
                target_point=target_point,
                text_value=request.input_text,
                key=request.key,
                modifiers=request.hotkey_modifiers,
                verify=True,
                expected_text=request.expected_mutation,
            )

            v_resp = await self.service.execute_action(v_req)

            exec_time_ms = (time.perf_counter() - start_time) * 1000
            verification = (
                HybridVerificationStatus.SUCCESS
                if v_resp.verification_status == VerificationStatus.VERIFIED
                else (
                    HybridVerificationStatus.FAILED
                    if v_resp.verification_status == VerificationStatus.FAILED
                    else HybridVerificationStatus.NOT_VERIFIED
                )
            )

            return InteractionResult(
                action_id=request.action_id,
                method=self.method,
                success=v_resp.success,
                execution_time_ms=exec_time_ms,
                verification_status=verification,
                verification_details=f"Visual action status: {v_resp.verification_status.value}",
                error_message=v_resp.error_message,
                mutation_detected=(v_resp.pixel_diff_percent > 0.05 if v_resp.pixel_diff_percent else False),
                metadata={"visual_action_id": v_resp.action_id},
            )
        except Exception as exc:
            exec_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error("Visual execution failed: %s", exc)
            return InteractionResult(
                action_id=request.action_id,
                method=self.method,
                success=False,
                execution_time_ms=exec_time_ms,
                verification_status=HybridVerificationStatus.FAILED,
                error_message=str(exc),
            )

    async def verify(self, action: InteractionAction, result: InteractionResult) -> HybridVerificationStatus:
        """Verify post-action visual state."""
        if not result.success:
            return HybridVerificationStatus.FAILED
        return result.verification_status
