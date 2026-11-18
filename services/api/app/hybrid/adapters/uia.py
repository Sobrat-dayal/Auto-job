"""Windows Microsoft UI Automation Interaction Adapter (Stage 17 Bridge)."""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from app.computer.contracts import DesktopActionType, ElementQuery
from app.computer.service import (
    DesktopActionRequest,
    DesktopAutomationService,
    InspectionOptions,
    desktop_service as default_desktop_service,
)
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

logger = logging.getLogger("autonom.hybrid.adapters.uia")


class WindowsUIAAdapter(BaseInteractionAdapter):
    """Adapter bridging native Microsoft UI Automation control into the Hybrid Engine."""

    def __init__(self, service: Optional[DesktopAutomationService] = None) -> None:
        super().__init__(method=InteractionMethod.WINDOWS_UIA)
        self._service = service or default_desktop_service

    @property
    def service(self) -> DesktopAutomationService:
        return self._service

    async def probe(self, target: InteractionTarget) -> CapabilityProbe:
        """Probe if target is an accessible native window or UIA element."""
        is_native_target = (
            target.target_type in (
                TargetType.NATIVE_APP,
                TargetType.NATIVE_WINDOW,
                TargetType.UIA_ELEMENT,
            )
            or target.surface_type == SurfaceType.NATIVE_UIA
            or bool(target.window_ref)
            or bool(target.window_handle)
            or bool(target.uia_runtime_id)
        )

        if not is_native_target:
            return CapabilityProbe(
                method=self.method,
                is_available=True,
                is_applicable=False,
                confidence_score=0.0,
                supported_actions=[],
                reason="Target is not associated with a native Windows application or UIA element",
            )

        supported_actions = [
            HybridActionType.CLICK.value,
            HybridActionType.DOUBLE_CLICK.value,
            HybridActionType.ENTER_TEXT.value,
            HybridActionType.SCROLL.value,
            HybridActionType.KEY_PRESS.value,
            HybridActionType.INSPECT.value,
            HybridActionType.SELECT_OPTION.value,
        ]

        if target.surface_type == SurfaceType.NATIVE_WIN32 and not target.uia_runtime_id:
            confidence = 0.50
        elif target.uia_runtime_id or target.element_name:
            confidence = 0.95
        else:
            confidence = 0.85

        return CapabilityProbe(
            method=self.method,
            is_available=True,
            is_applicable=True,
            confidence_score=confidence,
            supported_actions=supported_actions,
            required_permissions=["desktop:inspect", "desktop:interact"],
            resource_cost_score=2,  # Low-to-moderate cost
            latency_ms_estimate=30,
            verification_supported=True,
            reason="Native application with accessible UI Automation tree",
        )

    async def observe(self, request: ObservationRequest) -> InteractionObservation:
        """Inspect the accessibility tree of the native window."""
        target = request.target
        win_ref = target.window_ref

        if not win_ref and target.window_handle:
            win_ref = f"win_{target.window_handle}_{target.process_id or 0}"

        if not win_ref:
            # Fallback to active window
            windows = await self.service.list_windows()
            if windows:
                win_ref = windows[0].window_ref

        uia_summary = ""
        uia_elements: list[dict[str, Any]] = []

        if win_ref:
            try:
                tree_resp = await self.service.inspect_window_tree(
                    window_ref=win_ref,
                    options=InspectionOptions(max_depth=3, max_nodes=50),
                )
                uia_summary = f"Window: {tree_resp.root.name} ({tree_resp.total_nodes} nodes)"
                uia_elements = [
                    {
                        "element_ref": node.element_ref,
                        "name": node.name,
                        "control_type": node.control_type,
                        "is_enabled": node.is_enabled,
                    }
                    for node in tree_resp.nodes[:25]
                ]
            except Exception as exc:
                logger.warning("UIA tree inspection failed in adapter: %s", exc)
                uia_summary = f"Inspection error: {exc}"

        return InteractionObservation(
            target_id=target.target_id,
            method=self.method,
            surface_type=SurfaceType.NATIVE_UIA,
            observed_text=uia_summary,
            structure_summary=uia_summary,
            uia_elements=uia_elements,
            is_valid=True,
            is_stale=False,
        )

    async def execute(self, request: InteractionAction) -> InteractionResult:
        """Execute structural action via Microsoft UI Automation patterns."""
        start_time = time.perf_counter()
        target = request.target
        win_ref = target.window_ref

        if not win_ref and target.window_handle:
            win_ref = f"win_{target.window_handle}_{target.process_id or 0}"

        if not win_ref:
            windows = await self.service.list_windows()
            if windows:
                win_ref = windows[0].window_ref
            else:
                return InteractionResult(
                    action_id=request.action_id,
                    method=self.method,
                    success=False,
                    execution_time_ms=(time.perf_counter() - start_time) * 1000,
                    verification_status=HybridVerificationStatus.FAILED,
                    error_message="No active native window found for UIA execution",
                )

        # Map action type
        action_map = {
            HybridActionType.CLICK: DesktopActionType.INVOKE,
            HybridActionType.DOUBLE_CLICK: DesktopActionType.INVOKE,
            HybridActionType.ENTER_TEXT: DesktopActionType.SET_VALUE,
            HybridActionType.KEY_PRESS: DesktopActionType.PRESS_KEY,
            HybridActionType.SCROLL: DesktopActionType.SCROLL,
            HybridActionType.INSPECT: DesktopActionType.READ_TEXT,
            HybridActionType.SELECT_OPTION: DesktopActionType.SELECT,
        }

        uia_type = action_map.get(request.action_type, DesktopActionType.INVOKE)

        locator: Optional[ElementQuery] = None
        if target.element_name:
            locator = ElementQuery(name=target.element_name, control_type=target.control_type)
        elif target.uia_runtime_id:
            locator = ElementQuery(automation_id=target.uia_runtime_id)

        try:
            d_req = DesktopActionRequest(
                action_type=uia_type,
                window_ref=win_ref,
                element_ref=target.uia_runtime_id,
                locator=locator,
                value=request.input_text,
                key=request.key,
                modifiers=request.hotkey_modifiers,
                timeout_ms=request.timeout_ms,
                verify=True,
                expected_outcome=request.expected_mutation,
            )

            d_resp = await self.service.execute_action(d_req)

            exec_time_ms = (time.perf_counter() - start_time) * 1000
            verification = HybridVerificationStatus.SUCCESS if d_resp.verified else HybridVerificationStatus.FAILED

            return InteractionResult(
                action_id=request.action_id,
                method=self.method,
                success=d_resp.success,
                execution_time_ms=exec_time_ms,
                verification_status=verification,
                verification_details=f"UIA action status: {d_resp.action_id}, verified: {d_resp.verified}",
                error_message=d_resp.error_message,
                mutation_detected=d_resp.verified,
                metadata={"desktop_action_id": d_resp.action_id},
            )
        except Exception as exc:
            exec_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error("Windows UIA execution failed: %s", exc)
            return InteractionResult(
                action_id=request.action_id,
                method=self.method,
                success=False,
                execution_time_ms=exec_time_ms,
                verification_status=HybridVerificationStatus.FAILED,
                error_message=str(exc),
            )

    async def verify(self, action: InteractionAction, result: InteractionResult) -> HybridVerificationStatus:
        """Verify post-action UIA state."""
        if not result.success:
            return HybridVerificationStatus.FAILED
        return result.verification_status
