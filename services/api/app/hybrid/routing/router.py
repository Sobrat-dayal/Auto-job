"""Deterministic Hybrid Method Router for the Hybrid Computer Engine."""

from __future__ import annotations

import logging
from typing import Optional

from app.hybrid.adapters.registry import InteractionAdapterRegistry, get_adapter_registry
from app.hybrid.contracts import (
    CapabilityProbe,
    HybridActionType,
    InteractionMethod,
    InteractionTarget,
    RoutingDecisionRecordSchema,
    SurfaceType,
)
from app.hybrid.errors import NoEligibleMethodError
from app.hybrid.routing.health import MethodHealthTracker
from app.hybrid.routing.policies import RoutingPolicies
from app.hybrid.routing.scoring import MethodScorer
from app.hybrid.targets.classifier import SurfaceClassifier

logger = logging.getLogger("autonom.hybrid.routing.router")


class HybridMethodRouter:
    """Intelligent router selecting the optimal interaction method for any given target and action."""

    def __init__(
        self,
        registry: Optional[InteractionAdapterRegistry] = None,
        health_tracker: Optional[MethodHealthTracker] = None,
    ) -> None:
        self.registry = registry or get_adapter_registry()
        self.health_tracker = health_tracker or MethodHealthTracker()

    async def route(
        self,
        target: InteractionTarget,
        action_type: Optional[HybridActionType] = None,
        preferred_method: Optional[InteractionMethod] = None,
        task_id: Optional[str] = None,
    ) -> tuple[InteractionMethod, RoutingDecisionRecordSchema]:
        """Determine and explain the optimal interaction method for the target and action."""
        # 1. Ensure surface type is classified
        if not target.surface_type or target.surface_type == SurfaceType.UNKNOWN:
            target.surface_type = SurfaceClassifier.classify(target)

        # 2. Probe all registered adapters
        probes = await self.registry.probe_all(target)

        # 3. Filter candidates and track rejection reasons
        candidates: list[InteractionMethod] = []
        rejected: dict[str, str] = {}
        scores: dict[str, float] = {}

        preference_order = RoutingPolicies.get_preference_order(target.surface_type)

        for method, probe in probes.items():
            if not probe.is_available:
                rejected[method.value] = f"Adapter unavailable: {probe.reason}"
                continue
            if not probe.is_applicable:
                rejected[method.value] = f"Not applicable for target surface ({target.surface_type.value}): {probe.reason}"
                continue
            if action_type and action_type.value not in probe.supported_actions:
                rejected[method.value] = f"Action '{action_type.value}' is not supported by {method.value}"
                continue

            candidates.append(method)

        if not candidates:
            raise NoEligibleMethodError(
                f"No interaction method is eligible for target surface '{target.surface_type.value}' and action '{action_type}'.",
                details={
                    "target_id": target.target_id,
                    "surface_type": target.surface_type.value,
                    "rejected_methods": rejected,
                },
            )

        # 4. If operator requested a manual preference and it is eligible, honor it
        if preferred_method and preferred_method in candidates:
            probe = probes[preferred_method]
            health = self.health_tracker.get_status(preferred_method)
            score = MethodScorer.calculate_score(probe, health, is_preferred_order_rank=0)
            scores[preferred_method.value] = score

            decision = RoutingDecisionRecordSchema(
                task_id=task_id,
                target_id=target.target_id,
                selected_method=preferred_method,
                candidate_methods=candidates,
                rejected_methods=rejected,
                scoring=scores,
                rationale=f"Operator preferred method '{preferred_method.value}' selected and verified as applicable.",
            )
            return preferred_method, decision

        # 5. Score and rank all candidate methods
        for rank, method in enumerate(preference_order):
            if method in candidates:
                probe = probes[method]
                health = self.health_tracker.get_status(method)
                score = MethodScorer.calculate_score(probe, health, is_preferred_order_rank=rank)
                scores[method.value] = score

        # Sort candidates descending by score
        ranked_candidates = sorted(candidates, key=lambda m: scores.get(m.value, 0.0), reverse=True)
        selected = ranked_candidates[0]

        rationale = (
            f"Selected {selected.value} (score: {scores.get(selected.value, 0.0)}) for surface {target.surface_type.value}. "
            f"Preferred order: {[m.value for m in preference_order if m in candidates]}."
        )

        decision = RoutingDecisionRecordSchema(
            task_id=task_id,
            target_id=target.target_id,
            selected_method=selected,
            candidate_methods=candidates,
            rejected_methods=rejected,
            scoring=scores,
            rationale=rationale,
        )

        logger.info(
            "Hybrid routing decision: %s -> %s (candidates: %s)",
            target.target_id,
            selected.value,
            [m.value for m in candidates],
        )

        return selected, decision
