"""Specialist agents export for AUTONOM (Stage 13)."""

from app.orchestration.agents.specialists.automation import WorkflowAutomationAgent
from app.orchestration.agents.specialists.coding import CodingAgent
from app.orchestration.agents.specialists.computer import (
    BrowserAgent,
    StructuralUIAgent,
    VisualGroundingAgent,
    WindowsComputerAgent,
)
from app.orchestration.agents.specialists.creative_comms import CreativeAgent, MessagingAgent
from app.orchestration.agents.specialists.productivity import (
    DocumentAgent,
    PresentationAgent,
    SpreadsheetAgent,
)
from app.orchestration.agents.specialists.recruitment import (
    ApplicationAgent,
    InterviewPrepAgent,
    JobDiscoveryAgent,
    JobMatchingAgent,
    RecruitmentCommsAgent,
    ResumeAgent,
)
from app.orchestration.agents.specialists.research import (
    MarketIntelligenceAgent,
    ResearchAgent,
)

__all__ = [
    "JobDiscoveryAgent",
    "JobMatchingAgent",
    "ResumeAgent",
    "ApplicationAgent",
    "RecruitmentCommsAgent",
    "InterviewPrepAgent",
    "BrowserAgent",
    "WindowsComputerAgent",
    "VisualGroundingAgent",
    "StructuralUIAgent",
    "CodingAgent",
    "ResearchAgent",
    "MarketIntelligenceAgent",
    "DocumentAgent",
    "SpreadsheetAgent",
    "PresentationAgent",
    "CreativeAgent",
    "MessagingAgent",
    "WorkflowAutomationAgent",
]
