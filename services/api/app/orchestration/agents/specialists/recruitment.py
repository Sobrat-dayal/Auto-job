"""Recruitment specialist agents for AUTONOM (Stage 13)."""

import logging
from typing import Any

from app.orchestration.agents.base import SpecialistAgent
from app.orchestration.agents.contracts import AgentManifest, AgentRequest, AgentResult

logger = logging.getLogger("autonom.orchestration.agents.specialists.recruitment")


class JobDiscoveryAgent(SpecialistAgent):
    """Specialist agent for interpreting job search criteria and normalizing listings (Enhanced Stage 26)."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)

    async def execute_capability(
        self,
        capability_id: str,
        input_data: dict[str, Any],
        context: dict[str, Any],
    ) -> dict[str, Any]:
        """Dispatch discovery capability requests to JobDiscoveryAgentAdapter."""
        from app.recruitment.discovery.integrations.agents import job_discovery_agent_adapter

        if capability_id in ("job.discovery.list_sources", "job.search.sources"):
            enabled_only = input_data.get("enabled_only", True)
            return {"sources": job_discovery_agent_adapter.list_sources(enabled_only=enabled_only)}

        elif capability_id in ("job.discovery.fetch_source", "job.search.fetch"):
            source_id = input_data["source_id"]
            strategy_id = input_data.get("strategy_id")
            return await job_discovery_agent_adapter.fetch_source(source_id=source_id, strategy_id=strategy_id)

        elif capability_id in ("job.discovery.import_url", "job.import.url"):
            url = input_data["url"]
            employer = input_data.get("employer_name")
            target_role = input_data.get("target_role")
            return await job_discovery_agent_adapter.import_url(url=url, employer_name=employer, target_role=target_role)

        elif capability_id in ("job.discovery.import_manual", "job.import.manual"):
            return job_discovery_agent_adapter.import_manual(
                title=input_data["title"],
                employer_name=input_data["employer_name"],
                description=input_data["description"],
                source_url=input_data.get("source_url"),
                location=input_data.get("location"),
                work_arrangement=input_data.get("work_arrangement"),
                compensation_text=input_data.get("compensation_text"),
            )

        elif capability_id in ("job.discovery.start_task", "job.search.task"):
            source_ids = input_data.get("source_ids", [])
            strategy_id = input_data.get("strategy_id")
            return job_discovery_agent_adapter.start_discovery_task(source_ids=source_ids, strategy_id=strategy_id)

        elif capability_id in ("job.discovery.get_task_status", "job.search.status"):
            task_id = input_data["task_id"]
            status = job_discovery_agent_adapter.get_task_status(task_id)
            return status or {"task_id": task_id, "status": "not_found"}

        elif capability_id in ("job.discovery.get_summary", "job.search.summary"):
            return job_discovery_agent_adapter.get_discovery_summary()

        # Fallback to base registry
        return await super().execute_capability(capability_id, input_data, context)


class JobMatchingAgent(SpecialistAgent):
    """Specialist agent for extracting job requirements and matching applicant skills."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)


class ResumeAgent(SpecialistAgent):
    """Specialist agent for drafting tailored resume bullets strictly grounded in verified experience."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)


class ApplicationAgent(SpecialistAgent):
    """Specialist agent for categorizing application fields and drafting answers."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)


class RecruitmentCommsAgent(SpecialistAgent):
    """Specialist agent for summarizing recruiter interactions and drafting professional responses."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)


class InterviewPrepAgent(SpecialistAgent):
    """Specialist agent for generating tailored technical and behavioral interview preparation plans."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)
