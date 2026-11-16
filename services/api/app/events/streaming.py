"""Server-Sent Events (SSE) streaming adapter for real-time frontend updates."""

import asyncio
import logging
from collections.abc import AsyncGenerator
from datetime import UTC, datetime

from app.events.bus import EventBus

logger = logging.getLogger("autonom.streaming")


async def sse_event_generator(
    event_bus: EventBus,
    heartbeat_interval: float = 15.0,
) -> AsyncGenerator[str, None]:
    """Yields SSE formatted events from the EventBus, emitting periodic heartbeats during idle intervals."""
    logger.info("New SSE client connected to event stream.")

    queue: asyncio.Queue = asyncio.Queue(maxsize=100)
    async with event_bus._lock:
        event_bus._subscribers.add(queue)

    # Emit initial connection confirmation event after registering subscriber queue
    yield f": connected - {datetime.now(UTC).isoformat()}\n\n"

    try:
        while event_bus._is_running:
            try:
                event = await asyncio.wait_for(queue.get(), timeout=heartbeat_interval)
                yield event.to_sse_format()
                queue.task_done()
            except TimeoutError:
                yield f": ping - {datetime.now(UTC).isoformat()}\n\n"
    except (asyncio.CancelledError, GeneratorExit):
        logger.info("SSE client disconnected from event stream.")
    except Exception as exc:  # noqa: BLE001
        logger.warning(f"Error in SSE event stream: {exc}")
    finally:
        async with event_bus._lock:
            event_bus._subscribers.discard(queue)
        logger.info("Cleaned up SSE subscriber queue.")
