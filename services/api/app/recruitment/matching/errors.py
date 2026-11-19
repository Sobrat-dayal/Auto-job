"""Typed exceptions for Applicant-to-Job Matching Engine (Stage 29)."""

from __future__ import annotations


class MatchingError(Exception):
    """Base exception for all matching engine errors."""
    pass


class ApplicantProfileNotFoundError(MatchingError):
    """Raised when an applicant profile or snapshot cannot be resolved."""
    pass


class CanonicalJobNotFoundError(MatchingError):
    """Raised when a canonical job listing is missing from the database."""
    pass


class JobIntelligenceNotFoundError(MatchingError):
    """Raised when a job has not yet been processed by the Stage 28 intelligence engine."""
    pass


class CareerStrategyNotFoundError(MatchingError):
    """Raised when a requested career strategy does not exist."""
    pass


class EvaluationNotFoundError(MatchingError):
    """Raised when a match evaluation ID does not exist."""
    pass


class RubricNotFoundError(MatchingError):
    """Raised when a requested ranking rubric cannot be found."""
    pass


class HardPolicyViolationError(MatchingError):
    """Raised when a job violates an explicit hard restriction."""
    pass


class InvalidSnapshotError(MatchingError):
    """Raised when snapshot inputs fail version or schema validation."""
    pass


class MatchingAuthorizationError(MatchingError):
    """Raised when an agent lacks authorization for a matching capability."""
    pass


class SimulationError(MatchingError):
    """Raised when What-If scenario execution fails."""
    pass
