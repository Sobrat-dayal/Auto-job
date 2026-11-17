"""Creative and Communication specialist agents for AUTONOM (Stage 13)."""

import logging
from typing import Any

from app.orchestration.agents.base import SpecialistAgent
from app.orchestration.agents.contracts import AgentManifest

logger = logging.getLogger("autonom.orchestration.agents.specialists.creative_comms")


class CreativeAgent(SpecialistAgent):
    """Specialist agent for decomposing creative briefs into 3D scene specifications."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)


class MessagingAgent(SpecialistAgent):
    """Specialist agent for classifying messages, prioritizing urgency, and drafting replies."""

    def __init__(self, manifest: AgentManifest) -> None:
        super().__init__(manifest)
