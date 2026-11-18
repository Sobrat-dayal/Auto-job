"""Procedure Registry: versioning, immutability, publication, and import/export."""

from __future__ import annotations

import copy
from datetime import datetime, timezone
import json
import logging
from typing import Any, Dict, List, Optional

from app.computer.workflow_reliability.contracts import (
    ProcedureValidationStatus,
    ReusableProcedure,
)
from app.computer.workflow_reliability.errors import (
    ProcedureNotFoundError,
    ProcedureValidationError,
    ProcedureVersionConflictError,
)
from app.computer.workflow_reliability.procedures.validator import ProcedureValidator

logger = logging.getLogger("autonom.reliability.procedure_registry")


class ProcedureRegistry:
    """Manages persistent procedure versions, status lifecycles, and import/export."""

    def __init__(self) -> None:
        # Map: procedure_id -> { version_int: ReusableProcedure }
        self._procedures: Dict[str, Dict[int, ReusableProcedure]] = {}

    def register(self, procedure: ReusableProcedure) -> ReusableProcedure:
        """Register a new procedure or new version."""
        ProcedureValidator.validate(procedure)
        procedure.checksum = procedure.calculate_checksum()

        pid = procedure.procedure_id
        if pid not in self._procedures:
            self._procedures[pid] = {}

        # Enforce immutability if published version exists
        existing = self._procedures[pid].get(procedure.version)
        if existing and existing.validation_status == ProcedureValidationStatus.PUBLISHED:
            raise ProcedureVersionConflictError(
                f"Procedure '{pid}' version {procedure.version} is published and immutable. Create a new version."
            )

        self._procedures[pid][procedure.version] = procedure
        logger.info("Procedure registered: %s v%d (%s)", pid, procedure.version, procedure.name)
        return procedure

    def get(self, procedure_id: str, version: Optional[int] = None) -> Optional[ReusableProcedure]:
        """Retrieve procedure by ID and optional version (defaults to highest version)."""
        versions = self._procedures.get(procedure_id)
        if not versions:
            return None

        if version is not None:
            return versions.get(version)

        # Return latest version
        max_v = max(versions.keys())
        return versions[max_v]

    def list_all(self, category: Optional[str] = None) -> List[ReusableProcedure]:
        """List the latest version of all registered procedures."""
        results: List[ReusableProcedure] = []
        for pid, v_map in self._procedures.items():
            if not v_map:
                continue
            latest_v = max(v_map.keys())
            proc = v_map[latest_v]
            if category and proc.category != category:
                continue
            results.append(proc)
        return results

    def publish(self, procedure_id: str, version: Optional[int] = None) -> ReusableProcedure:
        """Publish a validated procedure version, making it immutable."""
        if version is None:
            latest = self.get(procedure_id)
            if not latest:
                raise ProcedureNotFoundError(f"Procedure '{procedure_id}' not found.")
            version = latest.version

        proc = self.get(procedure_id, version)
        if not proc:
            raise ProcedureNotFoundError(f"Procedure '{procedure_id}' v{version} not found.")

        ProcedureValidator.validate(proc)
        proc.validation_status = ProcedureValidationStatus.PUBLISHED
        proc.is_draft = False
        proc.updated_at = datetime.now(timezone.utc)
        logger.info("Procedure published: %s v%d", procedure_id, version)
        return proc

    def save_draft(self, procedure: ReusableProcedure) -> ReusableProcedure:
        """Alias for register to save a draft."""
        return self.register(procedure)

    def publish_version(self, procedure_id: str, version: Optional[int] = None) -> ReusableProcedure:
        """Alias for publish."""
        return self.publish(procedure_id, version)

    def branch_new_draft(self, procedure_id: str, from_version: Optional[int] = None) -> ReusableProcedure:
        """Branch a new draft version from an existing procedure."""
        base = self.get(procedure_id, from_version)
        if not base:
            raise ProcedureNotFoundError(f"Procedure '{procedure_id}' not found.")
        new_version = max(self._procedures[procedure_id].keys()) + 1
        draft = base.model_copy(deep=True)
        draft.version = new_version
        draft.is_draft = True
        draft.validation_status = ProcedureValidationStatus.DRAFT
        return self.register(draft)

    def deprecate(self, procedure_id: str, version: int) -> ReusableProcedure:
        """Mark a procedure version as deprecated."""
        proc = self.get(procedure_id, version)
        if not proc:
            raise ProcedureNotFoundError(f"Procedure '{procedure_id}' v{version} not found.")

        proc.validation_status = ProcedureValidationStatus.DEPRECATED
        proc.updated_at = datetime.now(timezone.utc)
        logger.info("Procedure deprecated: %s v%d", procedure_id, version)
        return proc

    def create_draft_version(self, procedure_id: str) -> ReusableProcedure:
        """Branch the latest procedure into a new draft version with incremented version number."""
        latest = self.get(procedure_id)
        if not latest:
            raise ProcedureNotFoundError(f"Procedure '{procedure_id}' not found.")

        new_version_num = latest.version + 1
        new_proc = copy.deepcopy(latest)
        new_proc.version = new_version_num
        new_proc.validation_status = ProcedureValidationStatus.DRAFT
        new_proc.created_at = datetime.now(timezone.utc)
        new_proc.updated_at = datetime.now(timezone.utc)

        return self.register(new_proc)

    def export_procedure(self, procedure_id: str, version: Optional[int] = None) -> str:
        """Export procedure definition to a portable declarative JSON format (no credentials)."""
        proc = self.get(procedure_id, version)
        if not proc:
            raise ProcedureNotFoundError(f"Procedure '{procedure_id}' not found.")

        data = proc.model_dump(mode="json")
        # Ensure no credential defaults leak
        for param in data.get("parameters", []):
            if param.get("sensitivity") == "SECRET":
                param["default_value"] = None

        return json.dumps(data, indent=2)

    def import_procedure(self, json_content: str) -> ReusableProcedure:
        """Import a declarative procedure definition from JSON with strict validation."""
        try:
            raw = json.loads(json_content)
        except Exception as exc:
            raise ProcedureValidationError(f"Malformed JSON payload: {exc}")

        # Block any executable code injections
        raw_str = json.dumps(raw).lower()
        if "__import__" in raw_str or "exec(" in raw_str or "eval(" in raw_str or "os.system" in raw_str:
            raise ProcedureValidationError("Arbitrary code injection detected in imported procedure definition.")

        proc = ReusableProcedure.model_validate(raw)
        # Import as DRAFT to mandate operator review before publication
        proc.validation_status = ProcedureValidationStatus.DRAFT
        return self.register(proc)
