"""Recruitment specialist agents for AUTONOM (Stage 13)."""

import logging
from typing import Any

from app.orchestration.agents.base import SpecialistAgent
from app.orchestration.agents.contracts import AgentManifest, AgentRequest, AgentResult

logger = logging.getLogger("autonom.orchestration.agents.specialists.recruitment")


class JobDiscoveryAgent(SpecialistAgent):
    """Specialist agent for interpreting job search criteria and normalizing listings."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)


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
