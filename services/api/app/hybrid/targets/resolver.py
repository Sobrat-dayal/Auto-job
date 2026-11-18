"""Target Resolver mapping application entities to Unified Interaction Targets."""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.browser.service import BrowserService
from app.computer.service import desktop_service
from app.hybrid.contracts import InteractionTarget, SurfaceType, TargetType
from app.hybrid.targets.classifier import SurfaceClassifier
from app.hybrid.targets.identity import TargetIdentityValidator

logger = logging.getLogger("autonom.hybrid.targets.resolver")


class TargetResolver:
    """Resolves natural language or partial target parameters into unified interaction targets."""

    def __init__(
        self,
        browser_svc: Optional[BrowserService] = None,
        desktop_svc: Optional[Any] = None,
    ) -> None:
        self._browser_svc = browser_svc
        self._desktop_svc = desktop_svc or desktop_service

    @property
    def browser(self) -> BrowserService:
        if self._browser_svc is None:
            self._browser_svc = BrowserService.get_instance()
        return self._browser_svc

    async def resolve(
        self,
        target_hint: Optional[str] = None,
        session_id: Optional[str] = None,
        dom_selector: Optional[str] = None,
        window_title: Optional[str] = None,
        window_handle: Optional[int] = None,
        coordinates: Optional[dict[str, Any]] = None,
        process_name: Optional[str] = None,
    ) -> InteractionTarget:
        """Resolve target metadata into a typed InteractionTarget."""
        target_type = TargetType.VISUAL_REGION
        surface_type = SurfaceType.UNKNOWN

        # 1. Browser target resolution
        if session_id or dom_selector:
            target_type = TargetType.BROWSER_ELEMENT if dom_selector else TargetType.BROWSER_PAGE
            target = InteractionTarget(
                target_type=target_type,
                session_id=session_id,
                dom_selector=dom_selector,
                element_name=target_hint,
            )
            target.surface_type = SurfaceClassifier.classify(target)
            return target

        # 2. Window title / HWND resolution
        if window_handle or window_title:
            matched_hwnd = window_handle
            proc_id: Optional[int] = None
            proc_name = process_name
            win_ref: Optional[str] = None

            try:
                windows = await self._desktop_svc.list_windows()
                for win in windows:
                    if (window_handle and win.hwnd == window_handle) or (
                        window_title and window_title.lower() in win.title.lower()
                    ):
                        matched_hwnd = win.hwnd
                        proc_id = win.process_id
                        proc_name = win.process_name
                        win_ref = win.window_ref
                        break
            except Exception as exc:
                logger.warning("Desktop window lookup failed during resolution: %s", exc)

            target = InteractionTarget(
                target_type=TargetType.NATIVE_WINDOW,
                window_handle=matched_hwnd,
                window_ref=win_ref,
                process_id=proc_id,
                process_name=proc_name,
                element_name=target_hint or window_title,
            )
            target.surface_type = SurfaceClassifier.classify(target)
            return target

        # 3. Coordinate resolution
        if coordinates:
            target = InteractionTarget(
                target_type=TargetType.VISUAL_CAPTURE_TARGET,
                surface_type=SurfaceType.CUSTOM_RENDERED,
                coordinates=coordinates,
                visual_target_name=target_hint,
            )
            return target

        # 4. Fallback to generic visual target with hint
        target = InteractionTarget(
            target_type=TargetType.VISUAL_REGION,
            surface_type=SurfaceType.UNKNOWN,
            visual_target_name=target_hint,
            element_name=target_hint,
        )
        target.surface_type = SurfaceClassifier.classify(target)
        return target
