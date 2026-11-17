"""Streaming coordinator delivering Server-Sent Events (SSE) token streams to desktop clients."""

import json
import logging
from typing import Any, AsyncIterator

from app.ai.cancellation import cancellation_manager
from app.ai.contracts import InferenceChunk, RoutingDecision

logger = logging.getLogger("autonom.ai.streaming")


def format_sse(event_type: str, data: dict[str, Any]) -> str:
    """Formats an SSE message frame."""
    payload = json.dumps(data, default=str)
    return f"event: {event_type}\ndata: {payload}\n\n"


class StreamingCoordinator:
    """Coordinates stream chunk formatting, error wrapping, and cancellation checks."""

    @staticmethod
    async def wrap_stream(
        request_id: str,
        routing_decision: RoutingDecision,
        chunk_iterator: AsyncIterator[InferenceChunk],
    ) -> AsyncIterator[str]:
        """Wraps provider chunk stream with lifecycle SSE events and cancellation guards."""
        # 1. Emit stream start event with routing decision
        yield format_sse(
            "start",
            {
                "request_id": request_id,
                "provider_id": routing_decision.selected_provider_id,
                "model_id": routing_decision.selected_model_id,
                "routing_decision": routing_decision.model_dump(),
            },
        )

        full_content = []
        token_count = 0
        final_usage = None

        try:
            async for chunk in chunk_iterator:
                # Check for client cancellation
                if cancellation_manager.is_cancelled(request_id):
                    logger.info(f"Stream '{request_id}' detected cancellation, terminating stream.")
                    yield format_sse("cancelled", {"request_id": request_id, "reason": "User cancelled generation."})
                    return

                if chunk.delta:
                    full_content.append(chunk.delta)
                    token_count += 1
                    yield format_sse("delta", {"request_id": request_id, "delta": chunk.delta})

                if chunk.usage:
                    final_usage = chunk.usage

            # Emit completion event
            yield format_sse(
                "complete",
                {
                    "request_id": request_id,
                    "content": "".join(full_content),
                    "finish_reason": "stop",
                    "usage": final_usage.model_dump()
                    if final_usage
                    else {"prompt_tokens": 0, "completion_tokens": token_count, "total_tokens": token_count},
                },
            )

        except Exception as exc:
            logger.error(f"Error in stream '{request_id}': {exc}")
            yield format_sse("error", {"request_id": request_id, "error": str(exc)})
