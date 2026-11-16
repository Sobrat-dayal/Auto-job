"""Pydantic schemas for event models and real-time streaming."""

from datetime import UTC, datetime
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, Field


class EventEnvelope(BaseModel):
    """Standardized event envelope used across the internal event bus and SSE streams."""

    event_id: str = Field(
        default_factory=lambda: f"evt-{uuid4().hex[:12]}",
        description="Globally unique event identifier",
    )
    event_type: str = Field(..., description="Dotted event topic name (e.g. task.progress, system.started)")
    timestamp: datetime = Field(
        default_factory=lambda: datetime.now(UTC),
        description="Event publication timestamp in UTC",
    )
    source: str = Field(default="autonom.backend", description="Component originating the event")
    correlation_id: str = Field(
        default_factory=lambda: f"cor-{uuid4().hex[:8]}",
        description="Correlation ID for end-to-end tracing",
    )
    task_id: str | None = Field(default=None, description="Associated task ID if task-scoped")
    schema_version: str = Field(default="1.0", description="Event schema version")
    payload: dict[str, Any] = Field(default_factory=dict, description="Typed payload dictionary")

    def to_sse_format(self) -> str:
        """Formats the event envelope into standard Server-Sent Events text."""
        json_payload = self.model_dump_json()
        return f"id: {self.event_id}\nevent: {self.event_type}\ndata: {json_payload}\n\n"
