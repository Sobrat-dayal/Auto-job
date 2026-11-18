"""Smart element locator resolution across accessibility trees (Stage 17)."""

import logging
from typing import Any

from app.computer.contracts import ElementQuery, UIElementInfo
from app.computer.uia.com_runtime import create_uia_client
from app.computer.uia.elements import CONTROL_TYPE_NAMES, element_extractor

logger = logging.getLogger("autonom.computer.uia.locators")


class LocatorResolver:
    """Resolves UI Automation elements using semantic locators (AutomationId, Name, ControlType, Class)."""

    @classmethod
    def find_elements(
        cls,
        hwnd: int,
        window_ref: str,
        query: ElementQuery,
        max_matches: int = 10,
    ) -> list[tuple[Any, UIElementInfo]]:
        """Finds matching COM elements and UIElementInfo records for a given query."""
        uia = create_uia_client()
        root_element = uia.ElementFromHandle(hwnd)

        walker = uia.ControlViewWalker
        matches: list[tuple[Any, UIElementInfo]] = []

        # Target criteria
        target_auto_id = query.automation_id.strip() if query.automation_id else None
        target_name = query.name.strip().lower() if query.name else None
        target_type = query.control_type.strip().lower() if query.control_type else None
        target_class = query.class_name.strip().lower() if query.class_name else None

        def _scan(element: Any, depth: int, index_path: str) -> None:
            if len(matches) >= max_matches or depth > 8:
                return

            try:
                el_info = element_extractor.extract_element_info(element, window_ref, index_path)

                is_match = True

                if target_auto_id:
                    if (el_info.automation_id or "").strip() != target_auto_id:
                        is_match = False

                if is_match and target_name:
                    el_name = (el_info.name or "").strip().lower()
                    if query.exact_name:
                        if el_name != target_name:
                            is_match = False
                    else:
                        if target_name not in el_name:
                            is_match = False

                if is_match and target_type:
                    if (el_info.control_type or "").lower() != target_type:
                        is_match = False

                if is_match and target_class:
                    if (el_info.class_name or "").lower() != target_class:
                        is_match = False

                if is_match and (target_auto_id or target_name or target_type or target_class):
                    matches.append((element, el_info))
                    if len(matches) >= max_matches:
                        return

                # Recurse children
                child = walker.GetFirstChildElement(element)
                child_idx = 0
                while child and len(matches) < max_matches:
                    _scan(child, depth + 1, f"{index_path}.{child_idx}")
                    child = walker.GetNextSiblingElement(child)
                    child_idx += 1
            except Exception as e:
                logger.debug(f"Element scan notice: {e}")

        _scan(root_element, 1, "0")
        return matches

    @classmethod
    def resolve_single_element(
        cls,
        hwnd: int,
        window_ref: str,
        query: ElementQuery,
    ) -> tuple[Any, UIElementInfo] | None:
        """Finds the single best match for a query. Returns None if not found."""
        matches = cls.find_elements(hwnd, window_ref, query, max_matches=2)
        if not matches:
            return None
        return matches[0]


locator_resolver = LocatorResolver()
