"""Real-time event streaming and event history endpoints."""

from fastapi import APIRouter
from fastapi.responses import StreamingResponse

from app.api.dependencies import AuthDep, EventBusDep
from app.events.streaming import sse_event_generator
from app.schemas.events import EventEnvelope

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/stream")
async def stream_events(
    event_bus: EventBusDep,
    _auth: AuthDep,
) -> StreamingResponse:
    """Streams live backend events to connected desktop frontend clients via Server-Sent Events."""
    return StreamingResponse(
        sse_event_generator(event_bus=event_bus),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/recent", response_model=list[EventEnvelope])
async def get_recent_events(
    event_bus: EventBusDep,
    _auth: AuthDep,
    limit: int = 50,
) -> list[EventEnvelope]:
    """Returns recent diagnostic events retained in the in-memory ring buffer."""
    return event_bus.get_recent_events(limit=limit)
