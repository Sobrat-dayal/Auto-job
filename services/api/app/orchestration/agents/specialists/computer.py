"""Computer control and visual/structural UI specialist agents for AUTONOM (Stage 13)."""

import logging
from typing import Any

from app.orchestration.agents.base import SpecialistAgent
from app.orchestration.agents.contracts import AgentManifest

logger = logging.getLogger("autonom.orchestration.agents.specialists.computer")


class BrowserAgent(SpecialistAgent):
    """Specialist agent for web navigation planning (Stage 16)."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)


class WindowsComputerAgent(SpecialistAgent):
    """Specialist agent for desktop automation planning (Stage 17-18)."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)


class VisualGroundingAgent(SpecialistAgent):
    """Specialist agent for image metadata and layout inspection."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)


class StructuralUIAgent(SpecialistAgent):
    """Specialist agent for accessibility tree node inspection."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)
