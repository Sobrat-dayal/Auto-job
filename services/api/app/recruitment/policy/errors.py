"""Domain errors for Recruitment Policy & Career Preferences Engine (Stage 25)."""

from typing import Optional


class RecruitmentPolicyError(Exception):
    """Base exception for all recruitment policy, eligibility, and preference operations."""

    def __init__(self, message: str, code: str = "POLICY_ERROR", details: Optional[dict] = None) -> None:
        super().__init__(message)
        self.message = message
        self.code = code
        self.details = details or {}


class CareerProfileNotFoundError(RecruitmentPolicyError):
    def __init__(self, profile_id: str) -> None:
        super().__init__(
            f"Career preference profile '{profile_id}' not found.",
            code="CAREER_PROFILE_NOT_FOUND",
            details={"profile_id": profile_id},
        )


class StrategyNotFoundError(RecruitmentPolicyError):
    def __init__(self, strategy_id: str) -> None:
        super().__init__(
            f"Career strategy '{strategy_id}' not found.",
            code="STRATEGY_NOT_FOUND",
            details={"strategy_id": strategy_id},
        )


class PolicyConflictError(RecruitmentPolicyError):
    def __init__(self, conflicts_count: int, message: str = "Contradictory policy rules detected.") -> None:
        super().__init__(
            f"{message} Found {conflicts_count} conflict(s).",
            code="POLICY_CONFLICT_DETECTED",
            details={"conflicts_count": conflicts_count},
        )


class EmployerBlockedError(RecruitmentPolicyError):
    def __init__(self, employer_name: str, reason: Optional[str] = None) -> None:
        super().__init__(
            f"Action prohibited: employer '{employer_name}' is explicitly on the blocklist. Reason: {reason or 'User-defined hard block'}",
            code="EMPLOYER_BLOCKED",
            details={"employer_name": employer_name, "reason": reason},
        )


class IneligibleJobError(RecruitmentPolicyError):
    def __init__(self, job_title: str, reason: str) -> None:
        super().__init__(
            f"Applicant is not eligible for job '{job_title}': {reason}",
            code="JOB_INELIGIBLE",
            details={"job_title": job_title, "reason": reason},
        )


class BudgetExceededError(RecruitmentPolicyError):
    def __init__(self, limit_type: str, limit_val: int, current_val: int) -> None:
        super().__init__(
            f"Application quota exceeded for {limit_type}. Max: {limit_val}, Current: {current_val}.",
            code="BUDGET_EXCEEDED",
            details={"limit_type": limit_type, "limit": limit_val, "current": current_val},
        )


class EmergencyStopActiveError(RecruitmentPolicyError):
    def __init__(self) -> None:
        super().__init__(
            "Recruitment operation blocked: Global Emergency Stop is currently engaged.",
            code="EMERGENCY_STOP_ENGAGED",
        )


class StandingGrantRevokedError(RecruitmentPolicyError):
    def __init__(self, grant_id: str) -> None:
        super().__init__(
            f"Standing grant '{grant_id}' has been revoked or expired.",
            code="GRANT_REVOKED",
            details={"grant_id": grant_id},
        )


class MissingAttestationError(RecruitmentPolicyError):
    def __init__(self, question_text: str) -> None:
        super().__init__(
            f"Privileged operation requires direct human attestation: '{question_text}'",
            code="ATTESTATION_REQUIRED",
            details={"question_text": question_text},
        )
