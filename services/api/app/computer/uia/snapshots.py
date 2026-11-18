"""Compact UI state snapshot serialization for LLM agent reasoning (Stage 17)."""

import logging
from app.computer.contracts import UITreeNode, UITreeSnapshot

logger = logging.getLogger("autonom.computer.uia.snapshots")


class UISnapshotCompiler:
    """Compiles structured UITreeSnapshots into compact text representations for AI reasoning."""

    @classmethod
    def compile_to_agent_prompt(cls, snapshot: UITreeSnapshot, max_chars: int = 4000) -> str:
        """Formats the accessibility tree snapshot into a concise, token-efficient text tree."""
        lines: list[str] = [
            f"=== WINDOW: {snapshot.title} ({snapshot.window_ref}) ===",
            f"Total Nodes: {snapshot.total_nodes} | Truncated: {snapshot.is_truncated}",
            "--- ACCESSIBILITY TREE ---",
        ]

        def _format_node(node: UITreeNode, indent_level: int) -> None:
            el = node.element
            indent = "  " * indent_level

            # Compact representation of attributes
            attrs = []
            if el.automation_id:
                attrs.append(f"id='{el.automation_id}'")
            if el.value:
                preview = el.value[:30] + "..." if len(el.value) > 30 else el.value
                attrs.append(f"val='{preview}'")
            if el.toggle_state:
                attrs.append(f"state={el.toggle_state}")
            if el.supported_patterns:
                pat_str = ",".join(el.supported_patterns)
                attrs.append(f"pat=[{pat_str}]")
            if not el.is_enabled:
                attrs.append("disabled")

            attr_suffix = f" ({', '.join(attrs)})" if attrs else ""
            name_part = f" '{el.name}'" if el.name else ""

            lines.append(f"{indent}[{el.control_type}]{name_part}{attr_suffix}")

            for child in node.children:
                _format_node(child, indent_level + 1)

        _format_node(snapshot.root, 0)
        full_text = "\n".join(lines)

        if len(full_text) > max_chars:
            return full_text[:max_chars] + f"\n... [Truncated for context limit, total nodes: {snapshot.total_nodes}]"

        return full_text


snapshot_compiler = UISnapshotCompiler()
