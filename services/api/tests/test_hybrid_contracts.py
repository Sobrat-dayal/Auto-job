"""Unit tests for Stage 19 Hybrid Computer Interaction contracts and schemas."""

import pytest
from app.hybrid.contracts import (
    ActionRiskLevel,
    CapabilityProbe,
    HybridActionType,
    HybridTaskStatus,
    HybridVerificationStatus,
    InteractionAction,
    InteractionMethod,
    InteractionObservation,
    InteractionResult,
    InteractionTarget,
    RoutingDecisionRecordSchema,
    SurfaceType,
    TargetType,
)


def test_interaction_target_aliases() -> None:
    """Verifies that hwnd and pid aliases are correctly remapped into standard target fields."""
    target = InteractionTarget.model_validate({
        "target_type": "NATIVE_WINDOW",
        "hwnd": 65536,
        "pid": 1024,
    })
    assert target.window_handle == 65536
    assert target.process_id == 1024
    assert target.target_id.startswith("tgt_")


def test_capability_probe_defaults() -> None:
    """Verifies default values and field validation for CapabilityProbe."""
    probe = CapabilityProbe(
        method=InteractionMethod.BROWSER_DOM,
        is_available=True,
        is_applicable=True,
        confidence_score=0.95,
        supported_actions=["click", "enter_text"],
        resource_cost_score=1,
    )
    assert probe.method == InteractionMethod.BROWSER_DOM
    assert probe.is_available is True
    assert probe.resource_cost_score == 1
    assert probe.latency_ms_estimate == 20


def test_interaction_action_and_result_contracts() -> None:
    """Verifies InteractionAction and InteractionResult instantiation and enum serialization."""
    target = InteractionTarget(
        target_type=TargetType.BROWSER_ELEMENT,
        surface_type=SurfaceType.BROWSER_DOM,
        dom_selector="button#submit",
    )
    action = InteractionAction(
        target=target,
        action_type=HybridActionType.CLICK,
        risk_level=ActionRiskLevel.REPEATABLE,
    )
    assert action.action_id.startswith("act_")
    assert action.action_type == HybridActionType.CLICK
    assert action.method is None

    result = InteractionResult(
        action_id=action.action_id,
        method=InteractionMethod.BROWSER_DOM,
        success=True,
        execution_time_ms=18.5,
        verification_status=HybridVerificationStatus.SUCCESS,
        mutation_detected=True,
    )
    assert result.success is True
    assert result.verification_status == HybridVerificationStatus.SUCCESS
    assert result.mutation_detected is True


def test_routing_decision_record_schema() -> None:
    """Verifies schema validation for explainable routing decisions."""
    record = RoutingDecisionRecordSchema(
        target_id="tgt_test_123",
        selected_method=InteractionMethod.BROWSER_DOM,
        candidate_methods=[InteractionMethod.BROWSER_DOM, InteractionMethod.VISUAL_GROUNDING],
        rejected_methods={"WINDOWS_UIA": "Target is web surface without native HWND"},
        scoring={"BROWSER_DOM": 92.5, "VISUAL_GROUNDING": 45.0},
        rationale="Selected BROWSER_DOM based on active Playwright context and valid DOM selector.",
    )
    assert record.decision_id.startswith("dec_")
    assert record.selected_method == InteractionMethod.BROWSER_DOM
    assert "WINDOWS_UIA" in record.rejected_methods
    assert record.scoring["BROWSER_DOM"] > record.scoring["VISUAL_GROUNDING"]
