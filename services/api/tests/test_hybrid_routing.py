"""Unit tests for the Hybrid Method Routing Engine covering the full Routing Test Matrix."""

import pytest
from app.hybrid.adapters.base import BaseInteractionAdapter
from app.hybrid.adapters.registry import InteractionAdapterRegistry
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
from app.hybrid.errors import NoEligibleMethodError
from app.hybrid.routing.router import HybridMethodRouter


class MockAdapter(BaseInteractionAdapter):
    """Mock adapter for controlled matrix testing."""

    def __init__(
        self,
        method: InteractionMethod,
        is_available: bool = True,
        is_applicable: bool = True,
        confidence_score: float = 1.0,
        supported_actions: list[str] | None = None,
        cost_score: int = 1,
    ) -> None:
        super().__init__(method=method)
        self._available = is_available
        self._applicable = is_applicable
        self._confidence = confidence_score
        self._supported_actions = supported_actions if supported_actions is not None else [
            "click", "enter_text", "navigate", "scroll", "inspect", "submit", "select_option"
        ]
        self._cost = cost_score

    async def probe(self, target: InteractionTarget) -> CapabilityProbe:
        return CapabilityProbe(
            method=self.method,
            is_available=self._available,
            is_applicable=self._applicable,
            confidence_score=self._confidence,
            supported_actions=self._supported_actions,
            resource_cost_score=self._cost,
        )

    async def observe(self, request: ObservationRequest) -> InteractionObservation:
        return InteractionObservation(
            target_id=request.target.target_id,
            method=self.method,
            surface_type=SurfaceType.BROWSER_DOM,
        )

    async def execute(self, request: InteractionAction) -> InteractionResult:
        return InteractionResult(
            action_id=request.action_id,
            method=self.method,
            success=True,
            verification_status=HybridVerificationStatus.SUCCESS,
        )

    async def verify(self, action: InteractionAction, result: InteractionResult) -> HybridVerificationStatus:
        return HybridVerificationStatus.SUCCESS


@pytest.fixture
def test_router() -> HybridMethodRouter:
    registry = InteractionAdapterRegistry()
    return HybridMethodRouter(registry=registry)


@pytest.mark.asyncio
async def test_scenario_a_browser_dom_priority(test_router: HybridMethodRouter) -> None:
    """Scenario A: Authorized browser page with accessible DOM control prefers BROWSER_DOM."""
    target = InteractionTarget(
        target_type=TargetType.BROWSER_ELEMENT,
        surface_type=SurfaceType.BROWSER_DOM,
        dom_selector="button#apply-job",
    )
    method, decision = await test_router.route(target=target, action_type=HybridActionType.CLICK)
    assert method == InteractionMethod.BROWSER_DOM
    assert decision.selected_method == InteractionMethod.BROWSER_DOM
    assert "Selected BROWSER_DOM" in decision.rationale


@pytest.mark.asyncio
async def test_scenario_b_native_uia_priority(test_router: HybridMethodRouter) -> None:
    """Scenario B: Native application with supported UIA control prefers WINDOWS_UIA."""
    target = InteractionTarget(
        target_type=TargetType.UIA_ELEMENT,
        surface_type=SurfaceType.NATIVE_UIA,
        uia_runtime_id="btn_submit_ok",
        element_name="Submit",
    )
    method, decision = await test_router.route(target=target, action_type=HybridActionType.CLICK)
    assert method == InteractionMethod.WINDOWS_UIA
    assert decision.selected_method == InteractionMethod.WINDOWS_UIA


@pytest.mark.asyncio
async def test_scenario_c_legacy_win32(test_router: HybridMethodRouter) -> None:
    """Scenario C: Legacy native control with Win32 HWND surface selects WINDOWS_WIN32."""
    target = InteractionTarget(
        target_type=TargetType.NATIVE_WINDOW,
        surface_type=SurfaceType.NATIVE_WIN32,
        window_handle=65536,
    )
    method, decision = await test_router.route(target=target, action_type=HybridActionType.CLICK)
    assert method == InteractionMethod.WINDOWS_WIN32


@pytest.mark.asyncio
async def test_scenario_d_custom_rendered_visual_priority(test_router: HybridMethodRouter) -> None:
    """Scenario D: Custom-rendered control with coordinates prefers VISUAL_GROUNDING."""
    target = InteractionTarget(
        target_type=TargetType.VISUAL_CAPTURE_TARGET,
        surface_type=SurfaceType.CUSTOM_RENDERED,
        coordinates={"x": 500, "y": 400},
    )
    method, decision = await test_router.route(target=target, action_type=HybridActionType.CLICK)
    assert method == InteractionMethod.VISUAL_GROUNDING


@pytest.mark.asyncio
async def test_scenario_e_method_unavailable_filtered_out() -> None:
    """Scenario E: Unavailable adapters are filtered out and not selected."""
    registry = InteractionAdapterRegistry()
    # Replace DOM adapter with unavailable one
    registry.register(MockAdapter(InteractionMethod.BROWSER_DOM, is_available=False))
    registry.register(MockAdapter(InteractionMethod.VISUAL_GROUNDING, is_available=True, is_applicable=True))
    router = HybridMethodRouter(registry=registry)

    target = InteractionTarget(
        target_type=TargetType.BROWSER_ELEMENT,
        surface_type=SurfaceType.BROWSER_DOM,
        dom_selector="button#ok",
    )
    method, decision = await router.route(target=target, action_type=HybridActionType.CLICK)
    # DOM was unavailable, so router fell back to eligible visual candidate
    assert method == InteractionMethod.VISUAL_GROUNDING
    assert "BROWSER_DOM" in decision.rejected_methods


@pytest.mark.asyncio
async def test_scenario_f_dom_and_visual_both_available_dom_wins() -> None:
    """Scenario F: DOM and Visual both available, DOM is selected due to higher structural reliability and lower cost."""
    registry = InteractionAdapterRegistry()
    registry.register(MockAdapter(InteractionMethod.BROWSER_DOM, is_available=True, is_applicable=True, cost_score=1))
    registry.register(MockAdapter(InteractionMethod.VISUAL_GROUNDING, is_available=True, is_applicable=True, cost_score=4))
    router = HybridMethodRouter(registry=registry)

    target = InteractionTarget(
        target_type=TargetType.BROWSER_ELEMENT,
        surface_type=SurfaceType.BROWSER_DOM,
        dom_selector="input#username",
    )
    method, decision = await router.route(target=target, action_type=HybridActionType.ENTER_TEXT)
    assert method == InteractionMethod.BROWSER_DOM
    assert decision.scoring["BROWSER_DOM"] > decision.scoring["VISUAL_GROUNDING"]


@pytest.mark.asyncio
async def test_scenario_g_uia_and_visual_both_available_uia_wins() -> None:
    """Scenario G: UIA and Visual both available on native surface, UIA is selected."""
    registry = InteractionAdapterRegistry()
    registry.register(MockAdapter(InteractionMethod.WINDOWS_UIA, is_available=True, is_applicable=True, cost_score=2))
    registry.register(MockAdapter(InteractionMethod.VISUAL_GROUNDING, is_available=True, is_applicable=True, cost_score=4))
    router = HybridMethodRouter(registry=registry)

    target = InteractionTarget(
        target_type=TargetType.UIA_ELEMENT,
        surface_type=SurfaceType.NATIVE_UIA,
        uia_runtime_id="btn_toggle",
    )
    method, decision = await router.route(target=target, action_type=HybridActionType.CLICK)
    assert method == InteractionMethod.WINDOWS_UIA


@pytest.mark.asyncio
async def test_scenario_h_uia_unsupported_visual_fallback() -> None:
    """Scenario H: UIA unsupported for specific action, routes to Visual Grounding."""
    registry = InteractionAdapterRegistry()
    registry.register(MockAdapter(
        InteractionMethod.WINDOWS_UIA,
        is_available=True,
        is_applicable=True,
        supported_actions=["click"],  # does not support right_click
    ))
    registry.register(MockAdapter(
        InteractionMethod.VISUAL_GROUNDING,
        is_available=True,
        is_applicable=True,
        supported_actions=["right_click"],
    ))
    router = HybridMethodRouter(registry=registry)

    target = InteractionTarget(
        target_type=TargetType.UIA_ELEMENT,
        surface_type=SurfaceType.NATIVE_UIA,
        uia_runtime_id="canvas_control",
    )
    method, decision = await router.route(target=target, action_type=HybridActionType.RIGHT_CLICK)
    assert method == InteractionMethod.VISUAL_GROUNDING
    assert "WINDOWS_UIA" in decision.rejected_methods


@pytest.mark.asyncio
async def test_scenario_i_manual_preference_respected(test_router: HybridMethodRouter) -> None:
    """Scenario I: Operator preferred method is respected if eligible."""
    target = InteractionTarget(
        target_type=TargetType.VISUAL_REGION,
        surface_type=SurfaceType.CUSTOM_RENDERED,
        coordinates={"x": 100, "y": 200},
    )
    method, decision = await test_router.route(
        target=target,
        action_type=HybridActionType.CLICK,
        preferred_method=InteractionMethod.VISUAL_GROUNDING,
    )
    assert method == InteractionMethod.VISUAL_GROUNDING
    assert "preferred method" in decision.rationale.lower()


@pytest.mark.asyncio
async def test_scenario_j_no_eligible_method_raises_error() -> None:
    """Scenario J: When all candidate methods are inapplicable or unsupported, raises NoEligibleMethodError."""
    registry = InteractionAdapterRegistry()
    registry.register(MockAdapter(InteractionMethod.BROWSER_DOM, is_applicable=False))
    registry.register(MockAdapter(InteractionMethod.WINDOWS_UIA, is_applicable=False))
    registry.register(MockAdapter(InteractionMethod.WINDOWS_WIN32, is_applicable=False))
    registry.register(MockAdapter(InteractionMethod.VISUAL_GROUNDING, is_applicable=False))
    router = HybridMethodRouter(registry=registry)

    target = InteractionTarget(target_type=TargetType.BROWSER_ELEMENT, surface_type=SurfaceType.UNKNOWN)
    with pytest.raises(NoEligibleMethodError):
        await router.route(target=target, action_type=HybridActionType.CLICK)
