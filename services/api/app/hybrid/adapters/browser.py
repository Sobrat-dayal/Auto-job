"""Browser DOM Interaction Adapter (Stage 16 Bridge)."""

from __future__ import annotations

import logging
import time
from typing import Any, Optional

from app.browser.service import (
    BrowserActionRequest,
    BrowserActionType,
    BrowserService,
    DOMInspectionRequest,
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

logger = logging.getLogger("autonom.hybrid.adapters.browser")


class BrowserDOMAdapter(BaseInteractionAdapter):
    """Adapter bridging Playwright and DOM-based automation into the Hybrid Engine."""

    def __init__(self, browser_service: Optional[BrowserService] = None) -> None:
        super().__init__(method=InteractionMethod.BROWSER_DOM)
        self._browser_service = browser_service

    @property
    def service(self) -> BrowserService:
        if self._browser_service is None:
            self._browser_service = BrowserService.get_instance()
        return self._browser_service

    async def probe(self, target: InteractionTarget) -> CapabilityProbe:
        """Probe if target is an accessible browser session, page, or DOM element."""
        # Check if target indicates browser context
        is_browser_target = (
            target.target_type in (
                TargetType.BROWSER_PAGE,
                TargetType.BROWSER_TAB,
                TargetType.BROWSER_FRAME,
                TargetType.BROWSER_ELEMENT,
            )
            or target.surface_type == SurfaceType.BROWSER_DOM
            or bool(target.dom_selector)
            or bool(target.session_id)
        )

        if not is_browser_target:
            return CapabilityProbe(
                method=self.method,
                is_available=True,
                is_applicable=False,
                confidence_score=0.0,
                supported_actions=[],
                reason="Target is not associated with an active browser context or DOM selector",
            )

        # Check browser runtime health
        runtime = self.service.get_runtime_status()
        is_available = bool(runtime.playwright_available and runtime.installed_browsers)

        supported_actions = [
            HybridActionType.CLICK.value,
            HybridActionType.DOUBLE_CLICK.value,
            HybridActionType.ENTER_TEXT.value,
            HybridActionType.NAVIGATE.value,
            HybridActionType.SCROLL.value,
            HybridActionType.KEY_PRESS.value,
            HybridActionType.INSPECT.value,
            HybridActionType.SUBMIT.value,
            HybridActionType.SELECT_OPTION.value,
        ]

        confidence = 0.95 if target.dom_selector else 0.85
        return CapabilityProbe(
            method=self.method,
            is_available=is_available,
            is_applicable=True,
            confidence_score=confidence,
            supported_actions=supported_actions,
            required_permissions=["browser:navigate", "browser:interact", "browser:read"],
            resource_cost_score=1,  # Lowest cost
            latency_ms_estimate=25,
            verification_supported=True,
            reason="Active browser context with valid DOM access",
        )

    async def observe(self, request: ObservationRequest) -> InteractionObservation:
        """Inspect DOM structure of the active tab or target."""
        target = request.target
        session_id = target.session_id
        page_id = target.page_id

        # If no explicit session is given, pick the first active session if available
        if not session_id:
            active_ids = list(self.service.session_manager.active_sessions.keys())
            if active_ids:
                session_id = active_ids[0]

        dom_summary = ""
        dom_elements: list[dict[str, Any]] = []

        if session_id:
            try:
                dom_resp = await self.service.inspect_dom(
                    session_id=session_id,
                    request=DOMInspectionRequest(
                        tab_id=page_id,
                        filter_interactive_only=True,
                        max_nodes=100,
                    ),
                )
                dom_summary = f"Page: {dom_resp.page_title} ({dom_resp.total_elements} elements)"
                dom_elements = [
                    {
                        "node_id": el.node_id,
                        "tag_name": el.tag_name,
                        "role": el.role,
                        "text": el.text_content,
                        "locator": el.primary_locator,
                    }
                    for el in dom_resp.interactive_elements[:30]
                ]
            except Exception as exc:
                logger.warning("DOM inspection failed in browser adapter: %s", exc)
                dom_summary = f"Inspection error: {exc}"

        return InteractionObservation(
            target_id=target.target_id,
            method=self.method,
            surface_type=SurfaceType.BROWSER_DOM,
            observed_text=dom_summary,
            structure_summary=dom_summary,
            dom_elements=dom_elements,
            is_valid=True,
            is_stale=False,
        )

    async def execute(self, request: InteractionAction) -> InteractionResult:
        """Execute action via Playwright DOM interaction."""
        start_time = time.perf_counter()
        target = request.target
        session_id = target.session_id

        if not session_id:
            active_ids = list(self.service.session_manager.active_sessions.keys())
            if active_ids:
                session_id = active_ids[0]
            else:
                return InteractionResult(
                    action_id=request.action_id,
                    method=self.method,
                    success=False,
                    execution_time_ms=(time.perf_counter() - start_time) * 1000,
                    verification_status=HybridVerificationStatus.FAILED,
                    error_message="No active browser session found for DOM execution",
                )

        # Map HybridActionType to BrowserActionType
        action_map = {
            HybridActionType.CLICK: BrowserActionType.CLICK,
            HybridActionType.DOUBLE_CLICK: BrowserActionType.CLICK,
            HybridActionType.ENTER_TEXT: BrowserActionType.FILL,
            HybridActionType.NAVIGATE: BrowserActionType.NAVIGATE,
            HybridActionType.SCROLL: BrowserActionType.SCROLL,
            HybridActionType.KEY_PRESS: BrowserActionType.PRESS_KEY,
            HybridActionType.INSPECT: BrowserActionType.INSPECT_DOM,
            HybridActionType.SUBMIT: BrowserActionType.CLICK,
            HybridActionType.SELECT_OPTION: BrowserActionType.SELECT,
        }

        b_type = action_map.get(request.action_type, BrowserActionType.CLICK)
        locator = target.dom_selector or "body"

        params: dict[str, Any] = {}
        if request.action_type == HybridActionType.ENTER_TEXT:
            params["value"] = request.input_text or ""
        elif request.action_type == HybridActionType.NAVIGATE:
            params["url"] = request.url or (request.input_text or "")
        elif request.action_type == HybridActionType.KEY_PRESS:
            params["key"] = request.key or "Enter"
        elif request.action_type == HybridActionType.SCROLL:
            params["direction"] = "down"
            params["delta_y"] = 300

        try:
            b_req = BrowserActionRequest(
                action_type=b_type,
                target_locator=locator,
                tab_id=target.page_id,
                parameters=params,
                timeout_ms=request.timeout_ms,
            )
            b_resp = await self.service.execute_action(session_id=session_id, request=b_req)

            exec_time_ms = (time.perf_counter() - start_time) * 1000
            success = (b_resp.status.value == "completed")
            verification = HybridVerificationStatus.SUCCESS if success else HybridVerificationStatus.FAILED

            return InteractionResult(
                action_id=request.action_id,
                method=self.method,
                success=success,
                execution_time_ms=exec_time_ms,
                verification_status=verification,
                verification_details=f"Browser action status: {b_resp.status.value}",
                error_message=b_resp.error_message,
                mutation_detected=success,
                metadata={"browser_action_id": b_resp.action_id},
            )
        except Exception as exc:
            exec_time_ms = (time.perf_counter() - start_time) * 1000
            logger.error("Browser DOM execution failed: %s", exc)
            return InteractionResult(
                action_id=request.action_id,
                method=self.method,
                success=False,
                execution_time_ms=exec_time_ms,
                verification_status=HybridVerificationStatus.FAILED,
                error_message=str(exc),
            )

    async def verify(self, action: InteractionAction, result: InteractionResult) -> HybridVerificationStatus:
        """Verify post-action DOM state."""
        if not result.success:
            return HybridVerificationStatus.FAILED
        return HybridVerificationStatus.SUCCESS
