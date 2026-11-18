"""Durable External Side-Effect Ledger and duplicate action prevention."""

from __future__ import annotations

import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from app.computer.workflow_reliability.contracts import ExternalSideEffect, SideEffectOutcome
from app.computer.workflow_reliability.errors import DuplicateSideEffectBlockedError

logger = logging.getLogger("autonom.reliability.side_effects")


class SideEffectLedger:
    """Tracks consequential external state mutations to prevent accidental duplication."""

    def __init__(self) -> None:
        # Map: effect_id -> ExternalSideEffect
        self._effects: Dict[str, ExternalSideEffect] = {}
        # Map: intent_hash -> effect_id (for fast duplicate detection)
        self._intents: Dict[str, str] = {}

    def compute_intent_hash(
        self,
        action_category: Optional[str] = None,
        destination: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        target_system: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> str:
        """Compute deterministic hash of an external action intent."""
        cat = action_category or operation or "general"
        dest = destination or target_system or "local"
        params = parameters or {}
        norm_params = json.dumps(params, sort_keys=True)
        payload = f"{cat}:{dest.lower().strip()}:{norm_params}"
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def record_intent(
        self,
        execution_id: str,
        step_id: str,
        action_category: Optional[str] = None,
        destination: Optional[str] = None,
        parameters: Optional[Dict[str, Any]] = None,
        idempotency_key: Optional[str] = None,
        side_effect_class: Optional[SideEffectClass] = None,
        target_system: Optional[str] = None,
        operation: Optional[str] = None,
        **kwargs: Any,
    ) -> ExternalSideEffect:
        """Record external operation intent before dispatching; raises DuplicateSideEffectBlockedError if duplicate."""
        cat = action_category or operation or "general"
        dest = destination or target_system or "local"
        params = parameters or {}
        intent_hash = self.compute_intent_hash(cat, dest, params)

        # Duplicate detection check
        existing_id = self._intents.get(intent_hash)
        if existing_id and existing_id in self._effects:
            existing = self._effects[existing_id]
            if existing.outcome in (SideEffectOutcome.CONFIRMED, SideEffectOutcome.DISPATCHED):
                raise DuplicateSideEffectBlockedError(
                    f"Duplicate external action blocked: '{cat}' to '{dest}' was already dispatched ({existing_id})."
                )

        effect = ExternalSideEffect(
            execution_id=execution_id,
            step_id=step_id,
            intent_id=intent_hash,
            idempotency_key=idempotency_key or f"idem_{intent_hash[:16]}",
            action_category=cat,
            destination=dest,
            target_system=dest,
            operation=cat,
            parameter_digest=intent_hash,
            outcome=SideEffectOutcome.DISPATCHED,
        )

        self._effects[effect.effect_id] = effect
        self._intents[intent_hash] = effect.effect_id

        logger.info(
            "External side effect recorded: %s (exec: %s, category: %s, dest: %s)",
            effect.effect_id,
            execution_id,
            cat,
            dest,
        )
        return effect

    def confirm_effect(self, effect_id: str, evidence: Optional[Dict[str, Any]] = None) -> ExternalSideEffect:
        """Confirm effect alias for confirm_outcome."""
        return self.confirm_outcome(effect_id, outcome=SideEffectOutcome.CONFIRMED, evidence=evidence or {})

    def confirm_outcome(
        self,
        effect_id: str,
        outcome: Any = SideEffectOutcome.CONFIRMED,
        evidence: Optional[Dict[str, Any]] = None,
    ) -> ExternalSideEffect:
        """Confirm or update observed outcome of an external operation."""
        if isinstance(outcome, dict):
            evidence = outcome
            outcome = SideEffectOutcome.CONFIRMED

        if effect_id not in self._effects:
            raise KeyError(f"Side effect '{effect_id}' not found.")

        effect = self._effects[effect_id]
        effect.outcome = outcome
        if evidence:
            effect.evidence.update(evidence)

        logger.info("External side effect outcome confirmed: %s -> %s", effect_id, getattr(outcome, "value", str(outcome)))
        return effect

    def get_execution_effects(self, execution_id: str) -> List[ExternalSideEffect]:
        """List all side effects recorded for an execution."""
        return [e for e in self._effects.values() if e.execution_id == execution_id]

    def has_unconfirmed_outcomes(self, execution_id: str) -> bool:
        """Check if an execution contains any unknown/unconfirmed side effects."""
        return any(
            e.outcome == SideEffectOutcome.UNKNOWN_OUTCOME or e.outcome == SideEffectOutcome.DISPATCHED
            for e in self.get_execution_effects(execution_id)
        )
