"""Immutable Policy Version Snapshots, SHA-256 Digesting, and Audit Lifecycle (Stage 25)."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime
from typing import Optional
from app.recruitment.policy.contracts import CareerStrategy, PolicyVersionSnapshot


class PolicyVersionManager:
    """Manages immutable version snapshots, cryptographic digests, and change audit histories for career policies."""

    def __init__(self) -> None:
        self._versions: dict[str, list[PolicyVersionSnapshot]] = {}  # strategy_id -> snapshots

    def create_snapshot(
        self,
        strategy: CareerStrategy,
        changelog: str = "Policy configuration updated.",
        author_id: str = "usr_01",
    ) -> PolicyVersionSnapshot:
        strategy_id = strategy.id
        current_history = self._versions.setdefault(strategy_id, [])
        version_num = len(current_history) + 1

        # Serialize strategy to canonical JSON dict
        snap_dict = strategy.model_dump(mode="json")
        dumped_str = json.dumps(snap_dict, sort_keys=True)
        sha256_hash = hashlib.sha256(dumped_str.encode("utf-8")).hexdigest()

        snapshot = PolicyVersionSnapshot(
            version=version_num,
            strategy_id=strategy_id,
            sha256_hash=sha256_hash,
            changelog=changelog,
            created_at=datetime.now(UTC),
            author_id=author_id,
            strategy_snapshot=snap_dict,
        )
        current_history.append(snapshot)
        return snapshot

    def get_version_history(self, strategy_id: str) -> list[PolicyVersionSnapshot]:
        return self._versions.get(strategy_id, [])

    def get_version(self, strategy_id: str, version: int) -> Optional[PolicyVersionSnapshot]:
        history = self._versions.get(strategy_id, [])
        for snap in history:
            if snap.version == version:
                return snap
        return None
