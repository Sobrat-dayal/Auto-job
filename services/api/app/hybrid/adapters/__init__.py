"""Hybrid interaction adapters package."""

from app.hybrid.adapters.base import BaseInteractionAdapter, InteractionAdapter
from app.hybrid.adapters.browser import BrowserDOMAdapter
from app.hybrid.adapters.registry import InteractionAdapterRegistry, get_adapter_registry
from app.hybrid.adapters.uia import WindowsUIAAdapter
from app.hybrid.adapters.visual import VisualAdapter
from app.hybrid.adapters.win32 import Win32Adapter

__all__ = [
    "InteractionAdapter",
    "BaseInteractionAdapter",
    "BrowserDOMAdapter",
    "WindowsUIAAdapter",
    "Win32Adapter",
    "VisualAdapter",
    "InteractionAdapterRegistry",
    "get_adapter_registry",
]
