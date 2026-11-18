"""Domain Exceptions for Resume Intelligence System (Stage 23)."""


class ResumeError(Exception):
    """Base exception for all resume operations."""
    pass


class ResumeNotFoundError(ResumeError):
    """Raised when a requested resume document cannot be found."""
    pass


class ResumeValidationError(ResumeError):
    """Raised when a resume or tailoring request fails validation."""
    pass


class ResumeVersionNotFoundError(ResumeError):
    """Raised when a specific resume version does not exist."""
    pass


class TemplateNotFoundError(ResumeError):
    """Raised when a specified resume template is not registered."""
    pass


class JobDescriptionNotFoundError(ResumeError):
    """Raised when a referenced job snapshot does not exist."""
    pass


class UnsupportedClaimError(ResumeError):
    """Raised when a generated or proposed bullet contains unverified facts."""
    pass


class DocumentExportError(ResumeError):
    """Raised when DOCX or PDF rendering/writing fails."""
    pass


class ATSValidationError(ResumeError):
    """Raised when ATS round-trip extraction fails critically."""
    pass


class PortfolioNotFoundError(ResumeError):
    """Raised when a requested portfolio cannot be found."""
    pass


class UnauthorizedResumeActionError(ResumeError):
    """Raised when an operation violates Stage 14 authorization boundaries."""
    pass
