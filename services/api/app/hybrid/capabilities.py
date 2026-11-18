"""Hybrid Computer Interaction Capabilities for Multi-Agent Orchestration."""

from __future__ import annotations

import logging
from typing import Any

from app.hybrid.contracts import (
    HybridActionType,
    HybridTaskRequest,
    InteractionAction,
    InteractionMethod,
    InteractionTarget,
    ObservationRequest,
)
from app.hybrid.service import hybrid_computer_service
from app.orchestration.capabilities.base import BaseCapability
from app.orchestration.contracts import VerificationPolicy

logger = logging.getLogger("autonom.hybrid.capabilities")


class HybridResolveTargetCapability(BaseCapability):
    """Capability resolving target hints into an InteractionTarget."""

    capability_id = "hybrid_resolve_target"
    name = "Resolve Hybrid Target"
    version = "1.0.0"
    description = "Resolves natural language or partial target parameters into a unified InteractionTarget."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 15
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_hint": {"type": "string"},
                "session_id": {"type": "string"},
                "dom_selector": {"type": "string"},
                "window_title": {"type": "string"},
                "window_handle": {"type": "integer"},
                "coordinates": {"type": "object"},
            },
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"target": {"type": "object"}},
            "required": ["target"],
        }

    async def execute(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        target = await hybrid_computer_service.resolve_target(
            target_hint=input_data.get("target_hint"),
            session_id=input_data.get("session_id"),
            dom_selector=input_data.get("dom_selector"),
            window_title=input_data.get("window_title"),
            window_handle=input_data.get("window_handle"),
            coordinates=input_data.get("coordinates"),
            process_name=input_data.get("process_name"),
        )
        return {"target": target.model_dump(mode="json")}


class HybridProbeMethodsCapability(BaseCapability):
    """Capability probing applicability of all interaction adapters."""

    capability_id = "hybrid_probe_methods"
    name = "Probe Hybrid Methods"
    version = "1.0.0"
    description = "Probes availability, applicability, and estimated cost for all interaction methods against a target."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 20
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"target": {"type": "object"}},
            "required": ["target"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"probes": {"type": "object"}},
            "required": ["probes"],
        }

    async def execute(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        target = InteractionTarget.model_validate(input_data["target"])
        probes = await hybrid_computer_service.probe_methods(target)
        return {"probes": {k: v.model_dump(mode="json") for k, v in probes.items()}}


class HybridRouteActionCapability(BaseCapability):
    """Capability predicting and explaining method routing."""

    capability_id = "hybrid_route_action"
    name = "Route Hybrid Action"
    version = "1.0.0"
    description = "Simulates and previews deterministic method routing for a target and action."
    requires_ai = False
    is_deterministic = True
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 15
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "object"},
                "action_type": {"type": "string"},
                "preferred_method": {"type": "string"},
            },
            "required": ["target"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"decision": {"type": "object"}},
            "required": ["decision"],
        }

    async def execute(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        target = InteractionTarget.model_validate(input_data["target"])
        act_type = HybridActionType(input_data["action_type"]) if "action_type" in input_data else None
        pref_method = InteractionMethod(input_data["preferred_method"]) if "preferred_method" in input_data else None

        decision = await hybrid_computer_service.preview_route(
            target=target,
            action_type=act_type,
            preferred_method=pref_method,
        )
        return {"decision": decision.model_dump(mode="json")}


class HybridObserveCapability(BaseCapability):
    """Capability capturing cross-method observations."""

    capability_id = "hybrid_observe"
    name = "Observe Target Surface"
    version = "1.0.0"
    description = "Captures normalized observations from the target surface across DOM, UIA, or visual signals."
    requires_ai = False
    is_deterministic = False
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = True

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target": {"type": "object"},
                "preferred_method": {"type": "string"},
                "include_snapshot": {"type": "boolean"},
                "include_visual": {"type": "boolean"},
            },
            "required": ["target"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"observation": {"type": "object"}},
            "required": ["observation"],
        }

    async def execute(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        target = InteractionTarget.model_validate(input_data["target"])
        pref_method = InteractionMethod(input_data["preferred_method"]) if "preferred_method" in input_data else None

        req = ObservationRequest(
            target=target,
            preferred_method=pref_method,
            include_snapshot=input_data.get("include_snapshot", True),
            include_visual=input_data.get("include_visual", False),
        )
        obs = await hybrid_computer_service.observe(req)
        return {"observation": obs.model_dump(mode="json")}


class HybridExecuteCapability(BaseCapability):
    """Capability executing a unified interaction action."""

    capability_id = "hybrid_execute"
    name = "Execute Hybrid Action"
    version = "1.0.0"
    description = "Executes a unified computer action (click, enter_text, scroll) with automatic routing and fallback."
    requires_ai = False
    is_deterministic = False
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 60
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"action": {"type": "object"}},
            "required": ["action"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"result": {"type": "object"}},
            "required": ["result"],
        }

    async def execute(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        action = InteractionAction.model_validate(input_data["action"])
        result = await hybrid_computer_service.execute_action(action)
        return {"result": result.model_dump(mode="json")}


class HybridClickCapability(BaseCapability):
    """Capability performing click on a resolved or hinted target."""

    capability_id = "hybrid_click"
    name = "Hybrid Click"
    version = "1.0.0"
    description = "Performs a click on an element across browser DOM, native UIA, or visual coordinates."
    requires_ai = False
    is_deterministic = False
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 30
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "target_hint": {"type": "string"},
                "preferred_method": {"type": "string"},
                "coordinates": {"type": "object"},
                "dom_selector": {"type": "string"},
                "window_title": {"type": "string"},
            },
            "required": ["target_hint"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"result": {"type": "object"}},
            "required": ["result"],
        }

    async def execute(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        target = await hybrid_computer_service.resolve_target(
            target_hint=input_data.get("target_hint"),
            dom_selector=input_data.get("dom_selector"),
            window_title=input_data.get("window_title"),
            coordinates=input_data.get("coordinates"),
        )
        pref_method = InteractionMethod(input_data["preferred_method"]) if "preferred_method" in input_data else None

        action = InteractionAction(
            target=target,
            action_type=HybridActionType.CLICK,
            method=pref_method,
        )
        result = await hybrid_computer_service.execute_action(action)
        return {"result": result.model_dump(mode="json")}


class HybridTypeCapability(BaseCapability):
    """Capability entering text into a resolved or hinted target."""

    capability_id = "hybrid_type"
    name = "Hybrid Type Text"
    version = "1.0.0"
    description = "Enters text into an input field across browser DOM, native UIA, or SendInput keyboard."
    requires_ai = False
    is_deterministic = False
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 45
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "text": {"type": "string"},
                "target_hint": {"type": "string"},
                "preferred_method": {"type": "string"},
                "dom_selector": {"type": "string"},
                "window_title": {"type": "string"},
            },
            "required": ["text"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"result": {"type": "object"}},
            "required": ["result"],
        }

    async def execute(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        target = await hybrid_computer_service.resolve_target(
            target_hint=input_data.get("target_hint"),
            dom_selector=input_data.get("dom_selector"),
            window_title=input_data.get("window_title"),
        )
        pref_method = InteractionMethod(input_data["preferred_method"]) if "preferred_method" in input_data else None

        action = InteractionAction(
            target=target,
            action_type=HybridActionType.ENTER_TEXT,
            method=pref_method,
            input_text=input_data["text"],
        )
        result = await hybrid_computer_service.execute_action(action)
        return {"result": result.model_dump(mode="json")}


class HybridFallbackCapability(BaseCapability):
    """Capability executing explicit method fallback."""

    capability_id = "hybrid_fallback"
    name = "Hybrid Fallback"
    version = "1.0.0"
    description = "Explicitly switches an action to an alternate interaction method when the initial method encounters an obstacle."
    requires_ai = False
    is_deterministic = False
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 60
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "action": {"type": "object"},
                "fallback_method": {"type": "string"},
            },
            "required": ["action", "fallback_method"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"result": {"type": "object"}},
            "required": ["result"],
        }

    async def execute(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        action = InteractionAction.model_validate(input_data["action"])
        action.method = InteractionMethod(input_data["fallback_method"])
        result = await hybrid_computer_service.execute_action(action)
        return {"result": result.model_dump(mode="json")}


class HybridExecuteTaskCapability(BaseCapability):
    """Capability running an end-to-end hybrid automation task."""

    capability_id = "hybrid_execute_task"
    name = "Execute Hybrid Task"
    version = "1.0.0"
    description = "Runs a multi-step or single-step computer task using the hybrid interaction engine."
    requires_ai = False
    is_deterministic = False
    default_verification_policy = VerificationPolicy.OUTPUT_CONTRACT
    timeout_seconds = 90
    idempotent = False

    @property
    def input_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {
                "instruction": {"type": "string"},
                "target": {"type": "object"},
                "preferred_method": {"type": "string"},
                "allow_fallback": {"type": "boolean"},
            },
            "required": ["instruction"],
        }

    @property
    def output_schema(self) -> dict[str, Any]:
        return {
            "type": "object",
            "properties": {"task": {"type": "object"}},
            "required": ["task"],
        }

    async def execute(self, input_data: dict[str, Any], context: dict[str, Any] | None = None) -> dict[str, Any]:
        pref_method = InteractionMethod(input_data["preferred_method"]) if "preferred_method" in input_data else None
        target = InteractionTarget.model_validate(input_data["target"]) if "target" in input_data else None

        task_req = HybridTaskRequest(
            instruction=input_data["instruction"],
            target=target,
            preferred_method=pref_method,
            allow_fallback=input_data.get("allow_fallback", True),
        )
        task_resp = await hybrid_computer_service.submit_task(task_req)
        return {"task": task_resp.model_dump(mode="json")}
