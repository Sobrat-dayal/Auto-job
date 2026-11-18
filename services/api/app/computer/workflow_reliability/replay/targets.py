"""Dynamic element re-resolution for procedure replay."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

from app.computer.workflow_reliability.errors import TargetReResolutionError

logger = logging.getLogger("autonom.reliability.target_resolver")


class DynamicTargetResolver:
    """Re-resolves stale recorded targets into live, verified interaction targets."""

    @staticmethod
    async def resolve_live_target(
        target_definition: Dict[str, Any],
        preferred_method: Optional[str] = None,
        hybrid_service: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """Dynamically re-resolve target for replay against live applications."""
        resolved = dict(target_definition)

        # 1. Browser DOM Target Re-resolution
        dom_selector = target_definition.get("dom_selector")
        if dom_selector:
            # Selector is kept semantic for live Playwright re-querying
            resolved["surface_type"] = "BROWSER_DOM"
            resolved["dom_selector"] = dom_selector.strip()
            logger.debug("Re-resolved browser target with selector: %s", dom_selector)
            return resolved

        # 2. Windows UIA Control Re-resolution
        element_name = target_definition.get("element_name") or target_definition.get("window_title")
        control_type = target_definition.get("control_type")
        uia_id = target_definition.get("uia_runtime_id")
        if element_name or control_type or uia_id:
            resolved["surface_type"] = "NATIVE_UIA"
            # Strip stale HWND from original recording; must resolve fresh HWND at runtime
            resolved.pop("window_handle", None)
            resolved["element_name"] = element_name
            resolved["control_type"] = control_type
            logger.debug("Re-resolved UIA control: %s (%s)", element_name, control_type)
            return resolved

        # 3. Visual Grounding Re-resolution
        visual_name = target_definition.get("visual_target_name") or target_definition.get("target_summary")
        if visual_name or "coordinates" in target_definition:
            resolved["surface_type"] = "VISUAL_GROUNDING"
            # Never reuse absolute historical coordinates without re-grounding
            resolved["re_ground_required"] = True
            resolved["visual_target_name"] = visual_name
            logger.debug("Marked visual target for fresh frame re-grounding: %s", visual_name)
            return resolved

        if not resolved:
            raise TargetReResolutionError("Cannot resolve target: Target definition is empty.")

        return resolved
