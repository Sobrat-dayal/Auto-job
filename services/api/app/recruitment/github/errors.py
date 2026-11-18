"""Domain exceptions for Stage 22 GitHub & Repository Intelligence."""

from __future__ import annotations


class GitHubIntelligenceError(Exception):
    """Base exception for all GitHub subsystem operations."""
    pass


class GitHubConnectionNotFoundError(GitHubIntelligenceError):
    """Raised when a specific connection ID does not exist."""
    pass


class GitHubRepositoryNotFoundError(GitHubIntelligenceError):
    """Raised when a requested repository cannot be found on GitHub or locally."""
    pass


class GitHubNotFoundError(GitHubIntelligenceError):
    """Raised when a generic requested GitHub resource cannot be found."""
    pass


class GitHubAuthenticationError(GitHubIntelligenceError):
    """Raised when GitHub token authentication fails or token is revoked."""
    pass


class GitHubPermissionDeniedError(GitHubIntelligenceError):
    """Raised when the connected token lacks required scopes (e.g. private repo access)."""
    pass


class GitHubRateLimitExceededError(GitHubIntelligenceError):
    """Raised when GitHub API primary or secondary rate limits are exhausted."""

    def __init__(self, message: str, reset_timestamp: int | None = None) -> None:
        super().__init__(message)
        self.reset_timestamp = reset_timestamp


class GitHubSourceAnalysisError(GitHubIntelligenceError):
    """Raised when repository source tree or file fetching/parsing fails."""
    pass


class CandidateNotFoundError(GitHubIntelligenceError):
    """Raised when a skill or project candidate ID is not found."""
    pass


class InvalidRepositoryURLError(GitHubIntelligenceError):
    """Raised when a repository URL is malformed or targets an untrusted domain."""
    pass
