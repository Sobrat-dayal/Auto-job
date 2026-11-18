"""Bounded frame buffer management and freshness verification (Stage 18)."""

from collections import deque
from datetime import UTC, datetime
import logging
from PIL import Image
from app.visual.contracts import CapturedFrame, FrameMetadata

logger = logging.getLogger("autonom.visual.capture.frames")


class FrameBuffer:
    """Thread-safe bounded FIFO queue prioritizing latest frames with backpressure dropping."""

    def __init__(self, max_capacity: int = 10, max_age_seconds: float = 5.0) -> None:
        self.max_capacity = max_capacity
        self.max_age_seconds = max_age_seconds
        self._frames: deque[tuple[CapturedFrame, Image.Image]] = deque(maxlen=max_capacity)

    def push_frame(self, frame: CapturedFrame, image: Image.Image) -> None:
        """Pushes a new frame into the buffer, discarding oldest if over capacity."""
        self._frames.append((frame, image))

    def get_latest(self) -> tuple[CapturedFrame, Image.Image] | None:
        """Returns the most recent frame and Pillow Image if available and fresh."""
        if not self._frames:
            return None
        return self._frames[-1]

    def is_latest_fresh(self) -> bool:
        """Verifies if the latest captured frame is within maximum freshness age threshold."""
        latest = self.get_latest()
        if not latest:
            return False
        meta = latest[0].metadata
        age = (datetime.now(UTC) - meta.timestamp).total_seconds()
        return age <= self.max_age_seconds

    def clear(self) -> None:
        """Clears all buffered frames."""
        self._frames.clear()

    @property
    def count(self) -> int:
        return len(self._frames)
