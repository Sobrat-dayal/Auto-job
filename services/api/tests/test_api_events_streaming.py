"""Unit and integration tests for Server-Sent Events (SSE) streaming and event retrieval."""

import pytest
from httpx import AsyncClient

from app.events.bus import EventBus
from app.events.models import EventType
from app.events.streaming import sse_event_generator
from app.schemas.events import EventEnvelope
from app.services.service_container import get_container


@pytest.mark.asyncio
async def test_sse_stream_unauthorized(async_client: AsyncClient):
    """Verifies that the /api/v1/events/stream endpoint rejects unauthenticated requests with 401."""
    response = await async_client.get("/api/v1/events/stream")
    assert response.status_code == 401
    data = response.json()
    assert data["error"]["code"] == "UNAUTHENTICATED"


@pytest.mark.asyncio
async def test_sse_event_generator_yields_events():
    """Directly tests that sse_event_generator yields the initial connection message and published events."""
    bus = EventBus(buffer_size=10)
    gen = sse_event_generator(event_bus=bus, heartbeat_interval=15.0)

    # First item yielded should be the initial connected confirmation comment
    first_item = await anext(gen)
    assert first_item.startswith(": connected - ")

    # Publish an event to the bus and verify the generator yields it in standard SSE format
    test_event = EventEnvelope(
        event_type=EventType.TASK_CREATED,
        task_id="tsk-unit-stream",
        payload={"message": "hello streaming"},
    )
    await bus.publish(test_event)

    second_item = await anext(gen)
    assert f"event: {EventType.TASK_CREATED}" in second_item
    assert "tsk-unit-stream" in second_item
    assert "data: " in second_item

    # Close generator
    await gen.aclose()
    await bus.close()


@pytest.mark.asyncio
async def test_recent_events_endpoint(async_client: AsyncClient, auth_headers: dict[str, str]):
    """Verifies the /api/v1/events/recent endpoint retrieves stored diagnostic events."""
    container = get_container()
    await container.event_bus.publish(
        EventEnvelope(event_type=EventType.SYSTEM_STARTED, payload={"status": "ok"})
    )

    response = await async_client.get("/api/v1/events/recent?limit=10", headers=auth_headers)
    assert response.status_code == 200
    events = response.json()
    assert isinstance(events, list)
    assert len(events) >= 1
    assert any(e["event_type"] == EventType.SYSTEM_STARTED for e in events)
