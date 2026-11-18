"""Domain exceptions for Applicant Profile Intelligence (Stage 21)."""


class ApplicantProfileError(Exception):
    """Base exception for all applicant profile subsystem operations."""
    pass


class ProfileNotFoundError(ApplicantProfileError):
    """Raised when an applicant profile ID does not exist."""
    pass


class ProfilePermissionDeniedError(ApplicantProfileError):
    """Raised when an actor lacks Stage 14 authorization to access or mutate profile data."""
    pass


class ClaimNotFoundError(ApplicantProfileError):
    """Raised when a specific claim ID is not found."""
    pass


class EvidenceNotFoundError(ApplicantProfileError):
    """Raised when an evidence document reference does not exist."""
    pass


class ImportJobNotFoundError(ApplicantProfileError):
    """Raised when an import batch ID is not found."""
    pass


class InvalidDocumentError(ApplicantProfileError):
    """Raised when an uploaded document cannot be parsed or violates size/type policies."""
    pass


class ExtractionFailedError(ApplicantProfileError):
    """Raised when candidate extraction fails to produce structured records."""
    pass


class ConcurrencyConflictError(ApplicantProfileError):
    """Raised when optimistic concurrency checks detect an intervening profile revision."""
    pass


class ConflictResolutionError(ApplicantProfileError):
    """Raised when an invalid claim conflict resolution is attempted."""
    pass
