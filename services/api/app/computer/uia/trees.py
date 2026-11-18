"""Bounded UI Automation tree inspection and serialization (Stage 17)."""

from datetime import UTC, datetime
import logging
from typing import Any

from app.computer.contracts import InspectionOptions, UITreeNode, UITreeSnapshot
from app.computer.uia.com_runtime import create_uia_client
from app.computer.uia.elements import element_extractor

logger = logging.getLogger("autonom.computer.uia.trees")


class UITreeInspector:
    """Inspects and serializes bounded accessibility trees for a target window."""

    @classmethod
    def inspect_window_tree(
        cls,
        hwnd: int,
        window_ref: str,
        title: str,
        options: InspectionOptions | None = None,
    ) -> UITreeSnapshot:
        """Synchronously traverses and serializes the UIA accessibility tree of a window."""
        if options is None:
            options = InspectionOptions()

        uia = create_uia_client()
        root_element = uia.ElementFromHandle(hwnd)

        walker = uia.ControlViewWalker if options.view_type == "control" else uia.RawViewWalker

        node_count = 0
        max_depth_reached = 0
        is_truncated = False

        def _traverse(element: Any, current_depth: int, index_path: str) -> UITreeNode | None:
            nonlocal node_count, max_depth_reached, is_truncated

            if node_count >= options.max_nodes:
                is_truncated = True
                return None

            node_count += 1
            if current_depth > max_depth_reached:
                max_depth_reached = current_depth

            el_info = element_extractor.extract_element_info(element, window_ref, index_path)

            children: list[UITreeNode] = []
            if current_depth < options.max_depth and node_count < options.max_nodes:
                try:
                    child = walker.GetFirstChildElement(element)
                    child_idx = 0
                    while child and node_count < options.max_nodes:
                        child_node = _traverse(child, current_depth + 1, f"{index_path}.{child_idx}")
                        if child_node:
                            children.append(child_node)
                        child = walker.GetNextSiblingElement(child)
                        child_idx += 1
                    if child and node_count >= options.max_nodes:
                        is_truncated = True
                except Exception as e:
                    logger.debug(f"Child traversal notice at {index_path}: {e}")

            return UITreeNode(element=el_info, children=children)

        root_node = _traverse(root_element, 1, "0")
        if not root_node:
            root_info = element_extractor.extract_element_info(root_element, window_ref, "0")
            root_node = UITreeNode(element=root_info, children=[])

        # Token estimation: approx 15 tokens per node in compact representation
        estimated_tokens = node_count * 15

        return UITreeSnapshot(
            window_ref=window_ref,
            title=title,
            root=root_node,
            total_nodes=node_count,
            max_depth_reached=max_depth_reached,
            is_truncated=is_truncated,
            estimated_tokens=estimated_tokens,
            inspected_at=datetime.now(UTC),
        )


tree_inspector = UITreeInspector()
