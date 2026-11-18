"""Stage 15 Memory synchronization and real-time event integration for Applicant Profiles."""

from __future__ import annotations

import logging
from typing import Any, Optional

from app.schemas.events import EventEnvelope

logger = logging.getLogger("autonom.recruitment.profile.integrations.memory")


class ProfileMemorySync:
    """Coordinates invalidation of semantic memory caches and publishes domain events."""

    @classmethod
    async def publish_event(cls, event_type: str, profile_id: str, data: Optional[dict[str, Any]] = None) -> None:
        """Publishes a typed event to the central event bus."""
        from app.services.service_container import get_container
        payload = {
            "profile_id": profile_id,
            **(data or {}),
        }
        try:
            container = get_container()
            if container and container.event_bus:
                await container.event_bus.publish(
                    EventEnvelope(
                        event_type=event_type,
                        source="autonom.recruitment.profile",
                        payload=payload,
                    )
                )
        except Exception as exc:
            logger.debug(f"Event bus dispatch notice ({event_type}): {exc}")

    @classmethod
    async def invalidate_stale_memories(cls, profile_id: str, updated_field: str) -> None:
        """Invalidates derived agent memories when a canonical profile record is edited or superseded."""
        logger.info(
            f"Invalidating semantic memory caches for profile '{profile_id}' on field '{updated_field}'"
        )
        await cls.publish_event(
            event_type="applicant.memory_invalidated",
            profile_id=profile_id,
            data={"field": updated_field, "action": "invalidate_cache"},
        )
