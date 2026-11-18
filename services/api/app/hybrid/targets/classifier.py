"""Target Surface Classifier for the Hybrid Computer Engine."""

from __future__ import annotations

import logging
from typing import Optional

from app.hybrid.contracts import InteractionTarget, SurfaceType, TargetType

logger = logging.getLogger("autonom.hybrid.targets.classifier")

# Common browser executable names
BROWSER_EXECUTABLES = {
    "chrome.exe",
    "msedge.exe",
    "brave.exe",
    "firefox.exe",
    "chromium.exe",
}

# Frameworks that often render custom/directX surfaces
CUSTOM_RENDER_CLASSES = {
    "UnityWndClass",
    "UnrealWindow",
    "DirectXWindowClass",
    "GLFW30",
    "SDL_app",
}


class SurfaceClassifier:
    """Classifies computer interaction surfaces to determine suitable interaction methods."""

    @staticmethod
    def classify(target: InteractionTarget) -> SurfaceType:
        """Determine the surface type of the target based on available evidence."""
        # 1. Explicit surface type if already determined
        if target.surface_type and target.surface_type != SurfaceType.UNKNOWN:
            return target.surface_type

        # 2. Browser DOM indicators
        if target.target_type in (
            TargetType.BROWSER_PAGE,
            TargetType.BROWSER_TAB,
            TargetType.BROWSER_FRAME,
            TargetType.BROWSER_ELEMENT,
        ):
            return SurfaceType.BROWSER_DOM

        if target.dom_selector or (target.session_id and not target.window_handle):
            return SurfaceType.BROWSER_DOM

        # Check process name for browser executable
        proc = (target.process_name or "").lower()
        if proc in BROWSER_EXECUTABLES and not target.uia_runtime_id:
            return SurfaceType.BROWSER_DOM

        # 3. Check for Custom Rendered / Game / DirectX / Canvas
        if target.target_type in (TargetType.VISUAL_CAPTURE_TARGET, TargetType.VISUAL_REGION):
            return SurfaceType.CUSTOM_RENDERED

        control_type = (target.control_type or "").lower()
        if control_type in ("custom", "pane") and target.coordinates and not target.element_name:
            return SurfaceType.CUSTOM_RENDERED

        # 4. Native UI Automation indicators
        if target.target_type == TargetType.UIA_ELEMENT or target.uia_runtime_id or target.element_name:
            return SurfaceType.NATIVE_UIA

        if target.window_ref or (target.window_handle and not target.dom_selector):
            return SurfaceType.NATIVE_UIA

        # 5. Legacy Win32 indicators
        if target.window_handle and target.window_handle > 0 and not target.uia_runtime_id:
            return SurfaceType.NATIVE_WIN32

        return SurfaceType.UNKNOWN
