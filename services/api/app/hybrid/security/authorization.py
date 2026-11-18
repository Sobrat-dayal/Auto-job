"""Authorization bridge evaluating Stage 14 permissions for hybrid actions."""

from __future__ import annotations

import logging
from typing import Optional

from app.hybrid.contracts import (
    HybridActionType,
    InteractionAction,
    InteractionMethod,
)
from app.hybrid.errors import FallbackBlockedError
from app.security.authorization.contracts import ActionEffect, AuthorizationDecision
from app.security.authorization.engine import (
    AuthorizationEngine,
    get_authorization_engine,
)

logger = logging.getLogger("autonom.hybrid.security.authorization")


class HybridAuthorizationBridge:
    """Enforces Stage 14 authorization boundaries for hybrid computer actions."""

    def __init__(self, auth_engine: Optional[AuthorizationEngine] = None) -> None:
        self._auth_engine = auth_engine or get_authorization_engine()

    def get_action_identifier(self, action_type: HybridActionType, method: InteractionMethod) -> tuple[str, str]:
        """Map action type and method to permission category and action identifier."""
        if method == InteractionMethod.BROWSER_DOM:
            if action_type == HybridActionType.NAVIGATE:
                return "browser", "browser_navigate"
            if action_type == HybridActionType.INSPECT:
                return "browser", "browser_inspect_dom"
            return "browser", "browser_click"

        if method in (InteractionMethod.WINDOWS_UIA, InteractionMethod.WINDOWS_WIN32):
            if action_type == HybridActionType.INSPECT:
                return "desktop", "desktop_inspect_tree"
            return "desktop", "desktop_invoke"

        if method == InteractionMethod.VISUAL_GROUNDING:
            if action_type == HybridActionType.INSPECT:
                return "desktop", "visual_capture_display"
            return "desktop", "visual_click"

        return "desktop", "hybrid_execute"

    async def authorize(
        self,
        subject_id: str,
        action: InteractionAction,
        method: InteractionMethod,
    ) -> AuthorizationDecision:
        """Evaluate authorization for an action using the specified method."""
        category, action_id = self.get_action_identifier(action.action_type, method)

        decision = await self._auth_engine.evaluate_authorization(
            subject_id=subject_id,
            category=category,
            action=action_id,
            resource=action.target.dom_selector or action.target.window_ref or action.target.target_id,
            parameters={
                "method": method.value,
                "action_type": action.action_type.value,
                "risk_level": action.risk_level.value,
            },
        )

        if decision.outcome != ActionEffect.ALLOW:
            logger.warning(
                "Hybrid action '%s' via %s denied: %s (outcome: %s)",
                action_id,
                method.value,
                decision.explanation,
                decision.outcome.value,
            )

        return decision

    async def validate_fallback_authorization(
        self,
        subject_id: str,
        action: InteractionAction,
        fallback_method: InteractionMethod,
    ) -> None:
        """Assert that fallback method does not bypass permissions or expand scope without authorization."""
        decision = await self.authorize(subject_id=subject_id, action=action, method=fallback_method)
        if decision.outcome != ActionEffect.ALLOW:
            raise FallbackBlockedError(
                f"Fallback to '{fallback_method.value}' is blocked by authorization policy: {decision.explanation}",
                details={"fallback_method": fallback_method.value, "reason": decision.explanation},
            )


# Global singleton instance
_auth_bridge: Optional[HybridAuthorizationBridge] = None


def get_hybrid_auth_bridge() -> HybridAuthorizationBridge:
    """Return shared HybridAuthorizationBridge singleton."""
    global _auth_bridge
    if _auth_bridge is None:
        _auth_bridge = HybridAuthorizationBridge()
    return _auth_bridge
