"""Coding specialist agent for AUTONOM (Stage 13)."""

import logging
from typing import Any

from app.orchestration.agents.base import SpecialistAgent
from app.orchestration.agents.contracts import AgentManifest

logger = logging.getLogger("autonom.orchestration.agents.specialists.coding")


class CodingAgent(SpecialistAgent):
    """Specialist agent for code explanation, static code review, bug identification, and test-case generation."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)
