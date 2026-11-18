"""Deterministic routing policies and preference rules for the Hybrid Engine."""

from __future__ import annotations

from typing import Optional

from app.hybrid.contracts import (
    ActionRiskLevel,
    CapabilityProbe,
    HybridActionType,
    InteractionMethod,
    InteractionTarget,
    SurfaceType,
)

# Standard deterministic preference ranking per surface type
DEFAULT_PREFERENCE_ORDER: dict[SurfaceType, list[InteractionMethod]] = {
    SurfaceType.BROWSER_DOM: [
        InteractionMethod.BROWSER_DOM,
        InteractionMethod.WINDOWS_UIA,
        InteractionMethod.VISUAL_GROUNDING,
    ],
    SurfaceType.NATIVE_UIA: [
        InteractionMethod.WINDOWS_UIA,
        InteractionMethod.WINDOWS_WIN32,
        InteractionMethod.VISUAL_GROUNDING,
    ],
    SurfaceType.NATIVE_WIN32: [
        InteractionMethod.WINDOWS_WIN32,
        InteractionMethod.WINDOWS_UIA,
        InteractionMethod.VISUAL_GROUNDING,
    ],
    SurfaceType.CUSTOM_RENDERED: [
        InteractionMethod.VISUAL_GROUNDING,
        InteractionMethod.WINDOWS_UIA,
    ],
    SurfaceType.EMBEDDED_WEBVIEW: [
        InteractionMethod.BROWSER_DOM,
        InteractionMethod.WINDOWS_UIA,
        InteractionMethod.VISUAL_GROUNDING,
    ],
    SurfaceType.UNKNOWN: [
        InteractionMethod.WINDOWS_UIA,
        InteractionMethod.BROWSER_DOM,
        InteractionMethod.VISUAL_GROUNDING,
    ],
}

# Actions considered non-idempotent or irreversible
NON_IDEMPOTENT_ACTIONS = {
    HybridActionType.SUBMIT,
}


class RoutingPolicies:
    """Evaluates deterministic priority, safety gates, and action idempotency."""

    @staticmethod
    def get_preference_order(surface_type: SurfaceType) -> list[InteractionMethod]:
        """Return the ordered preference list for the specified surface."""
        return DEFAULT_PREFERENCE_ORDER.get(surface_type, DEFAULT_PREFERENCE_ORDER[SurfaceType.UNKNOWN])

    @staticmethod
    def is_action_non_idempotent(action_type: HybridActionType, risk_level: ActionRiskLevel) -> bool:
        """Determine if an action is non-idempotent and unsafe to blindly replay on fallback."""
        if risk_level in (ActionRiskLevel.NON_IDEMPOTENT, ActionRiskLevel.IRREVERSIBLE):
            return True
        return action_type in NON_IDEMPOTENT_ACTIONS
