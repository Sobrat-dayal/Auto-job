"""Reconciliation package for conflict detection and source authority."""

from app.recruitment.intelligence.reconciliation.authority import get_source_authority
from app.recruitment.intelligence.reconciliation.conflicts import detect_multi_source_conflicts

__all__ = [
    "detect_multi_source_conflicts",
    "get_source_authority",
]
