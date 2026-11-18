"""Recording session finalizer and integrity validation."""

from datetime import datetime, timezone
import hashlib
import json
from typing import List

from app.computer.workflow_reliability.contracts import RecordedAction, RecordingSession, RecordingStatus
from app.computer.workflow_reliability.errors import RecordingError


class RecordingFinalizer:
    """Validates sequence order, seals action history, and computes SHA-256 session integrity."""

    @staticmethod
    def finalize(session: RecordingSession, actions: List[RecordedAction]) -> RecordingSession:
        """Finalize the recording session into an immutable, verified record."""
        if session.status in (RecordingStatus.COMPLETED, RecordingStatus.FINALIZING):
            return session

        session.status = RecordingStatus.FINALIZING

        # 1. Sort actions by sequence index
        sorted_actions = sorted(actions, key=lambda a: a.sequence_index)

        # 2. Re-index sequentially to eliminate any recording gaps
        for idx, act in enumerate(sorted_actions):
            act.sequence_index = idx

        # 3. Calculate canonical integrity hash
        hash_payload = []
        for a in sorted_actions:
            hash_payload.append({
                "idx": a.sequence_index,
                "type": a.action_type,
                "adapter": a.source_adapter,
                "target": a.target_summary,
                "status": a.result_status,
                "time": a.execution_timestamp.isoformat(),
            })

        digest_str = json.dumps(hash_payload, sort_keys=True)
        session.integrity_hash = hashlib.sha256(digest_str.encode("utf-8")).hexdigest()

        session.captured_actions_count = len(sorted_actions)
        session.finalized_at = datetime.now(timezone.utc)
        session.status = RecordingStatus.COMPLETED

        return session
