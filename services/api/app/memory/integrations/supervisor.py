"""Supervisor and Multi-Agent Orchestration Memory Integrations for Stage 15."""

import logging
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from app.memory.contracts import ContextBuildRequest, ContextBuildResponse, MemoryType, SearchMode
from app.memory.service import memory_service

logger = logging.getLogger("autonom.memory.integrations.supervisor")


class SupervisorMemoryIntegration:
    """Enriches supervisor workflow planning and recovery with contextual memory."""

    async def get_planning_context(
        self,
        goal: str,
        workflow_id: Optional[str] = None,
        max_tokens: int = 1500,
    ) -> ContextBuildResponse:
        """Retrieves verified skills, reusable procedures, and prior workflow experiences relevant to goal."""
        req = ContextBuildRequest(
            task_description=goal,
            agent_role="supervisor",
            workflow_id=workflow_id,
            max_tokens=max_tokens,
            memory_types=[MemoryType.SEMANTIC, MemoryType.PROCEDURAL, MemoryType.EPISODIC],
        )
        return await memory_service.build_context(req)

    async def record_workflow_experience(
        self,
        workflow_id: str,
        goal: str,
        success: bool,
        lessons: str,
        scope_id: str = "default_user",
    ) -> None:
        """Persists a structured episodic memory after workflow conclusion."""
        from app.memory.contracts import (
            ConfidenceCategory,
            MemoryCreateRequest,
            MemoryScope,
            SensitivityCategory,
            VerificationStatus,
        )

        title = f"Workflow Outcome: {goal[:50]}"
        content = f"Workflow '{workflow_id}' {'succeeded' if success else 'failed'}. Notes/Lessons: {lessons}"

        req = MemoryCreateRequest(
            memory_type=MemoryType.EPISODIC,
            title=title,
            content=content,
            summary=f"Result for '{goal[:40]}'",
            owner_scope=MemoryScope.WORKFLOW,
            scope_id=scope_id,
            source_type="task_execution",
            source_ref=workflow_id,
            verification_status=VerificationStatus.VERIFIED if success else VerificationStatus.EVIDENCE_SUPPORTED,
            confidence_category=ConfidenceCategory.HIGH,
            sensitivity_category=SensitivityCategory.INTERNAL,
        )
        await memory_service.write_memory(req, actor_id="supervisor", workflow_id=workflow_id)
        logger.info(f"Recorded workflow episodic memory for '{workflow_id}'")


supervisor_memory = SupervisorMemoryIntegration()
