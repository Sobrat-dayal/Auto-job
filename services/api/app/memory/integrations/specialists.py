"""Specialist agent memory scopes and contextual retrieval integrations."""

import logging
from typing import Optional

from app.memory.contracts import (
    ContextBuildRequest,
    ContextBuildResponse,
    MemoryScope,
    MemorySearchRequest,
    MemorySearchResultItem,
    MemoryType,
    SearchMode,
)
from app.memory.service import memory_service

logger = logging.getLogger("autonom.memory.integrations.specialists")


class SpecialistMemoryIntegration:
    """Provides role-bounded memory retrieval for recruitment, coding, research, and creative agents."""

    async def get_recruitment_facts(
        self,
        query: str,
        applicant_id: str = "default_applicant",
        limit: int = 5,
    ) -> list[MemorySearchResultItem]:
        """Retrieves authorized applicant profile facts, verified technical skills, and career preferences."""
        req = MemorySearchRequest(
            query=query,
            search_mode=SearchMode.HYBRID,
            owner_scope=MemoryScope.APPLICANT_PROFILE,
            scope_id=applicant_id,
            memory_types=[MemoryType.SEMANTIC],
            limit=limit,
            exclude_superseded=True,
        )
        res = await memory_service.search_memory(req, actor_id="recruitment_agent")
        return res.results

    async def get_coding_context(
        self,
        task: str,
        project_id: str = "default_project",
        max_tokens: int = 1500,
    ) -> ContextBuildResponse:
        """Retrieves authorized code conventions, architectural patterns, and verified bug resolutions."""
        req = ContextBuildRequest(
            task_description=task,
            agent_role="coding_agent",
            max_tokens=max_tokens,
            scope_ids=[project_id],
            memory_types=[MemoryType.SEMANTIC, MemoryType.PROCEDURAL],
        )
        return await memory_service.build_context(req)

    async def get_research_findings(
        self,
        topic: str,
        project_id: str = "default_project",
        limit: int = 5,
    ) -> list[MemorySearchResultItem]:
        """Retrieves verified research notes, cited documents, and previous findings."""
        req = MemorySearchRequest(
            query=topic,
            search_mode=SearchMode.HYBRID,
            owner_scope=MemoryScope.PROJECT,
            scope_id=project_id,
            memory_types=[MemoryType.SEMANTIC],
            limit=limit,
        )
        res = await memory_service.search_memory(req, actor_id="research_agent")
        return res.results


specialist_memory = SpecialistMemoryIntegration()
