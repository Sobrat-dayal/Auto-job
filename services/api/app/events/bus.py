"""Asynchronous in-memory event bus with subscriber isolation and ring-buffered history."""

import asyncio
import logging
from collections import deque
from collections.abc import AsyncGenerator

from app.core.config import settings
from app.schemas.events import EventEnvelope

logger = logging.getLogger("autonom.events")


class EventBus:
    """Decoupled asynchronous event bus.

    Supports fan-out delivery to multiple subscribers, bounded ring-buffer history,
    and subscriber isolation ensuring slow or stalled consumers never block execution.
    """

    def __init__(self, buffer_size: int | None = None) -> None:
        self.buffer_size = buffer_size or settings.event_buffer_size
        self._subscribers: set[asyncio.Queue[EventEnvelope]] = set()
        self._history: deque[EventEnvelope] = deque(maxlen=self.buffer_size)
        self._lock = asyncio.Lock()
        self._is_running = True

    @property
    def subscriber_count(self) -> int:
        """Returns the current number of active event subscribers."""
        return len(self._subscribers)

    async def publish(self, event: EventEnvelope) -> None:
        """Publishes an event to all active subscriber queues without blocking execution."""
        if not self._is_running:
            logger.debug(f"Event bus stopped; dropped event {event.event_type} ({event.event_id})")
            return

        async with self._lock:
            self._history.append(event)
            active_subs = list(self._subscribers)

        dead_subs = []
        for queue in active_subs:
            try:
                # Attempt non-blocking put; if queue is saturated, discard oldest to avoid hanging
                if queue.full():
                    try:
                        queue.get_nowait()
                    except asyncio.QueueEmpty:
                        pass
                queue.put_nowait(event)
            except Exception as exc:  # noqa: BLE001
                logger.warning(f"Failed delivering event {event.event_id} to subscriber: {exc}")
                dead_subs.append(queue)

        if dead_subs:
            async with self._lock:
                for dead in dead_subs:
                    self._subscribers.discard(dead)

    async def subscribe(self, maxsize: int = 100) -> AsyncGenerator[EventEnvelope, None]:
        """Subscribes to all event bus messages with automated cleanup on consumer exit."""
        queue: asyncio.Queue[EventEnvelope] = asyncio.Queue(maxsize=maxsize)
        async with self._lock:
            self._subscribers.add(queue)

        try:
            while self._is_running:
                event = await queue.get()
                yield event
                queue.task_done()
        finally:
            async with self._lock:
                self._subscribers.discard(queue)

    def get_recent_events(self, limit: int = 50) -> list[EventEnvelope]:
        """Returns the most recent events retained in the ring buffer."""
        events = list(self._history)
        return events[-limit:]

    async def close(self) -> None:
        """Closes the event bus and cleans up subscriber queues."""
        self._is_running = False
        async with self._lock:
            self._subscribers.clear()
            self._history.clear()
        logger.info("Event bus closed.")
