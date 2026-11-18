"""Recruitment Writing Domain Exceptions (Stage 24)."""

from __future__ import annotations


class WritingDomainError(Exception):
    """Base exception for recruitment writing domain."""
    pass


class CoverLetterNotFoundError(WritingDomainError):
    """Raised when a cover letter cannot be found."""
    pass


class QuestionSetNotFoundError(WritingDomainError):
    """Raised when an application question set cannot be found."""
    pass


class QuestionNotFoundError(WritingDomainError):
    """Raised when a specific question within a set is missing."""
    pass


class AnswerValidationError(WritingDomainError):
    """Raised when an application answer fails typing, length, or option validation."""
    pass


class FactGroundingViolationError(WritingDomainError):
    """Raised when a writing draft makes ungrounded claims not backed by verified profile facts."""
    pass


class SensitiveDecisionRequiredError(WritingDomainError):
    """Raised when an action attempts to auto-answer or bypass explicit user consent for sensitive questions."""
    pass


class AttestationRequiredError(WritingDomainError):
    """Raised when legal certification or attestation lacks explicit human approval."""
    pass


class PackageNotReadyError(WritingDomainError):
    """Raised when an application writing package is approved while unresolved errors or missing items remain."""
    pass


class WritingExportError(WritingDomainError):
    """Raised when document compilation or round-trip validation fails."""
    pass
