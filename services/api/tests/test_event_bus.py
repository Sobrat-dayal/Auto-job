"""Unit tests for EventBus publication, subscriptions, and isolation."""

import asyncio

import pytest

from app.events.bus import EventBus
from app.events.models import EventType
from app.schemas.events import EventEnvelope


@pytest.mark.asyncio
async def test_publish_and_subscribe_single():
    bus = EventBus(buffer_size=10)
    received = []

    async def reader():
        async for evt in bus.subscribe():
            received.append(evt)
            if len(received) >= 2:
                break

    task = asyncio.create_task(reader())
    await asyncio.sleep(0.01)

    evt1 = EventEnvelope(event_type=EventType.TASK_CREATED, payload={"num": 1})
    evt2 = EventEnvelope(event_type=EventType.TASK_STARTED, payload={"num": 2})

    await bus.publish(evt1)
    await bus.publish(evt2)

    await asyncio.wait_for(task, timeout=2.0)
    assert len(received) == 2
    assert received[0].event_type == EventType.TASK_CREATED
    assert received[1].event_type == EventType.TASK_STARTED
    await bus.close()


@pytest.mark.asyncio
async def test_fanout_multiple_subscribers():
    bus = EventBus(buffer_size=10)
    sub1_events = []
    sub2_events = []

    async def sub1():
        async for evt in bus.subscribe():
            sub1_events.append(evt)
            if len(sub1_events) >= 1:
                break

    async def sub2():
        async for evt in bus.subscribe():
            sub2_events.append(evt)
            if len(sub2_events) >= 1:
                break

    t1 = asyncio.create_task(sub1())
    t2 = asyncio.create_task(sub2())
    await asyncio.sleep(0.01)

    assert bus.subscriber_count == 2
    await bus.publish(EventEnvelope(event_type=EventType.SYSTEM_STARTED, payload={"status": "ok"}))

    await asyncio.wait_for(asyncio.gather(t1, t2), timeout=2.0)
    assert len(sub1_events) == 1
    assert len(sub2_events) == 1
    assert sub1_events[0].event_type == EventType.SYSTEM_STARTED
    await bus.close()


@pytest.mark.asyncio
async def test_slow_subscriber_does_not_block():
    bus = EventBus(buffer_size=5)
    # A tiny queue subscriber that never reads
    queue: asyncio.Queue = asyncio.Queue(maxsize=1)
    async with bus._lock:
        bus._subscribers.add(queue)

    # Publishing multiple events should not hang
    for i in range(5):
        await bus.publish(EventEnvelope(event_type=EventType.TASK_PROGRESS, payload={"step": i}))

    assert len(bus.get_recent_events()) == 5
    await bus.close()
