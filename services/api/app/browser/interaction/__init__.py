"""Browser interaction and DOM manipulation package."""

from app.browser.interaction.locators import LocatorResolver
from app.browser.interaction.dom import DOMExtractor
from app.browser.interaction.actions import ActionExecutor
from app.browser.interaction.forms import FormAnalyzer
from app.browser.interaction.verification import ActionVerifier

__all__ = [
    "LocatorResolver",
    "DOMExtractor",
    "ActionExecutor",
    "FormAnalyzer",
    "ActionVerifier",
]
