"""Memory consolidation service merging compatible evidence and extracting reusable procedures."""

from datetime import UTC, datetime
import logging
from typing import Any, Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.contracts import (
    ConfidenceCategory,
    MemoryScope,
    MemoryType,
    ProvenanceMetadata,
    SensitivityCategory,
    VerificationStatus,
)
from app.memory.storage.repository import MemoryRepository

logger = logging.getLogger("autonom.memory.lifecycle.consolidation")


class MemoryConsolidator:
    """Consolidates working/episodic memories into durable facts and extracts procedural templates."""

    async def consolidate_scope(
        self,
        session: AsyncSession,
        scope_id: str,
        owner_scope: MemoryScope = MemoryScope.USER,
    ) -> dict[str, Any]:
        """Runs bounded consolidation over active memories in a scope."""
        repo = MemoryRepository(session)
        records = await repo.list_memories(scope_id=scope_id, limit=50)

        consolidated_count = 0
        cleaned_up = 0

        # Group by topic/title
        grouped: dict[str, list[Any]] = {}
        for r in records:
            key = r.title.strip().lower()
            grouped.setdefault(key, []).append(r)

        for _topic, group in grouped.items():
            if len(group) > 1:
                # Keep the newest verified or evidence-supported record, supersede others
                sorted_group = sorted(
                    group,
                    key=lambda x: (
                        1 if x.verification_status in ("verified", "user_confirmed") else 0,
                        x.created_at,
                    ),
                    reverse=True,
                )
                winner = sorted_group[0]
                for loser in sorted_group[1:]:
                    if loser.verification_status != VerificationStatus.SUPERSEDED.value:
                        await repo.update_memory(
                            loser.id,
                            {
                                "verification_status": VerificationStatus.SUPERSEDED.value,
                                "superseded_by": winner.id,
                            },
                        )
                        consolidated_count += 1

        return {
            "scope_id": scope_id,
            "consolidated_records": consolidated_count,
            "cleaned_up": cleaned_up,
        }

    async def extract_procedure_from_workflow(
        self,
        session: AsyncSession,
        workflow_id: str,
        procedure_name: str,
        capability_id: str,
        steps: list[dict[str, Any]],
        provenance: Optional[dict[str, Any]] = None,
    ) -> Optional[str]:
        """Extracts and registers a reusable procedural memory from a successfully verified workflow run."""
        repo = MemoryRepository(session)
        proc_id = f"proc_{uuid.uuid4().hex[:8]}"

        sanitized_steps = []
        for i, step in enumerate(steps, 1):
            sanitized_steps.append(
                {
                    "step_number": i,
                    "name": step.get("name", f"Step {i}"),
                    "action": step.get("action", capability_id),
                    "capability_id": step.get("capability_id", capability_id),
                    "parameters_template": step.get("parameters", {}),
                }
            )

        procedure = await repo.create_procedure(
            procedure_id=proc_id,
            name=procedure_name,
            description=f"Automated procedure extracted from workflow '{workflow_id}'",
            capability_id=capability_id,
            required_inputs={"workflow_id": workflow_id},
            steps=sanitized_steps,
            preconditions={"authorized_run": True},
            expected_outputs={"success": True},
            verification_requirements={"output_contract": True},
            required_permissions=[f"capability:{capability_id}"],
            provenance=provenance or {"workflow_id": workflow_id, "extracted_at": datetime.now(UTC).isoformat()},
        )
        logger.info(f"Extracted procedural memory '{procedure.procedure_id}' ({procedure.name})")
        return procedure.procedure_id


# Global singleton consolidator
memory_consolidator = MemoryConsolidator()
