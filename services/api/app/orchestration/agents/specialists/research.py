"""Research and Market Intelligence specialist agents for AUTONOM (Stage 13)."""

import logging
from typing import Any

from app.orchestration.agents.base import SpecialistAgent
from app.orchestration.agents.contracts import AgentManifest

logger = logging.getLogger("autonom.orchestration.agents.specialists.research")


class ResearchAgent(SpecialistAgent):
    """Specialist agent for synthesizing reference documents and comparing research evidence."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)


class MarketIntelligenceAgent(SpecialistAgent):
    """Specialist agent for analyzing supplied market datasets, competitor benchmarks, and metrics."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)
