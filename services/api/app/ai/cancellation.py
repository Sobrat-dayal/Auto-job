"""Cooperative cancellation coordinator for active inference requests."""

import asyncio
import logging

logger = logging.getLogger("autonom.ai.cancellation")


class CancellationManager:
    """Manages active request cancellation tokens and clean cooperative termination."""

    def __init__(self) -> None:
        self._tokens: dict[str, asyncio.Event] = {}

    def register(self, request_id: str) -> asyncio.Event:
        """Registers a new cancellation event token for a request."""
        event = asyncio.Event()
        self._tokens[request_id] = event
        return event

    def unregister(self, request_id: str) -> None:
        """Removes the cancellation token when request terminates."""
        self._tokens.pop(request_id, None)

    def cancel(self, request_id: str) -> bool:
        """Triggers cancellation on the registered request token."""
        event = self._tokens.get(request_id)
        if event and not event.is_set():
            logger.info(f"Cancellation requested for inference request '{request_id}'")
            event.set()
            return True
        return False

    def is_cancelled(self, request_id: str) -> bool:
        """Checks if cancellation has been requested."""
        event = self._tokens.get(request_id)
        return event.is_set() if event else False


cancellation_manager = CancellationManager()
