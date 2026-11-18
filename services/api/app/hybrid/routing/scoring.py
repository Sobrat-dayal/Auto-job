"""Transparent method scoring model for the Hybrid Engine."""

from __future__ import annotations

from app.hybrid.contracts import CapabilityProbe, InteractionMethod, MethodHealthStatus


class MethodScorer:
    """Scores candidate methods across capability fit, reliability, resource efficiency, and history."""

    @staticmethod
    def calculate_score(
        probe: CapabilityProbe,
        health: MethodHealthStatus,
        is_preferred_order_rank: int = 0,
    ) -> float:
        """Calculate a composite score from 0.0 to 100.0 for a candidate method."""
        if not probe.is_available or not probe.is_applicable:
            return 0.0

        # 1. Capability Fit (0..35 pts)
        fit_score = probe.confidence_score * 35.0

        # 2. Structural Reliability Base (0..25 pts)
        reliability_map = {
            InteractionMethod.BROWSER_DOM: 25.0,
            InteractionMethod.WINDOWS_UIA: 22.0,
            InteractionMethod.WINDOWS_WIN32: 15.0,
            InteractionMethod.VISUAL_GROUNDING: 10.0,
        }
        rel_score = reliability_map.get(probe.method, 10.0)

        # 3. Resource Cost Efficiency (0..20 pts)
        # resource_cost_score is 1 (cheapest) to 5 (most expensive)
        cost_pts = max(0.0, (6.0 - probe.resource_cost_score) * 4.0)

        # 4. Preference Order Bonus (0..25 pts)
        order_bonus = max(0.0, 25.0 - (is_preferred_order_rank * 10.0))

        # 5. Historical Success Penalty / Bonus (0..5 pts)
        total_hist = health.success_count + health.failure_count
        hist_score = 5.0
        if total_hist > 0:
            success_rate = health.success_count / total_hist
            hist_score = success_rate * 5.0

        total = fit_score + rel_score + cost_pts + order_bonus + hist_score
        return round(min(100.0, max(0.0, total)), 2)
