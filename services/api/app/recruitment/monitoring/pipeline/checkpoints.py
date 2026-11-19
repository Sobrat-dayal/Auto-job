"""Checkpoint state manager for durable monitoring run recovery."""

from __future__ import annotations

from typing import Any
from app.recruitment.monitoring.contracts import PipelinePhase


class CheckpointState:
    def __init__(self, data: dict[str, Any] | None = None) -> None:
        self.data = data or {}

    def set_phase(self, phase: PipelinePhase) -> None:
        self.data["current_phase"] = phase.value

    def mark_completed_source(self, source_id: str) -> None:
        completed = set(self.data.get("completed_sources", []))
        completed.add(source_id)
        self.data["completed_sources"] = list(completed)

    def is_source_completed(self, source_id: str) -> bool:
        return source_id in self.data.get("completed_sources", [])

    def record_checkpoint(self, key: str, value: Any) -> None:
        self.data[key] = value

    def to_dict(self) -> dict[str, Any]:
        return dict(self.data)
