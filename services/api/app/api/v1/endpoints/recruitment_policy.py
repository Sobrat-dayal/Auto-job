"""FastAPI REST API Endpoints for Career Preferences & Recruitment Policy Engine (Stage 25)."""

from __future__ import annotations

from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from app.api.dependencies import AuthDep
from app.core.security import AuthContext
from app.recruitment.policy.contracts import (
    BudgetReservationRequest,
    BudgetReservationResponse,
    CareerPreferenceProfile,
    CareerStrategy,
    CareerStrategyCreateRequest,
    CareerStrategyUpdateRequest,
    JobPolicyEvaluationRequest,
    PolicyConflictItem,
    PolicySimulationRequest,
    PolicySimulationResponse,
    PolicyVersionSnapshot,
    RecruitmentBudget,
    RecruitmentDecision,
    ReviewQueueItem,
    ReviewResolutionRequest,
    StandingGrantRecord,
)
from app.recruitment.policy.errors import (
    CareerProfileNotFoundError,
    RecruitmentPolicyError,
    StrategyNotFoundError,
)
from app.recruitment.policy.rules.engine import PolicyRulesEngine
from app.recruitment.policy.service import recruitment_policy_service

router = APIRouter(prefix="/recruitment", tags=["Recruitment Policy & Career Preferences"])


# =============================================================================
# Career Strategies & Preferences
# =============================================================================

@router.get("/career-strategies", response_model=list[CareerStrategy])
async def list_career_strategies(
    auth: AuthDep,
) -> list[CareerStrategy]:
    """Lists all configured career strategies for the applicant."""
    return recruitment_policy_service.list_strategies()


@router.post("/career-strategies", response_model=CareerStrategy, status_code=status.HTTP_201_CREATED)
async def create_career_strategy(
    request: CareerStrategyCreateRequest,
    auth: AuthDep,
) -> CareerStrategy:
    """Creates a new career strategy with custom role, location, compensation, and employer rules."""
    return recruitment_policy_service.create_strategy(request, auth_context=auth)


@router.get("/career-strategies/{strategy_id}", response_model=CareerStrategy)
async def get_career_strategy(
    strategy_id: str,
    auth: AuthDep,
) -> CareerStrategy:
    """Retrieves specific career strategy details."""
    strat = recruitment_policy_service.get_strategy(strategy_id)
    if not strat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Strategy '{strategy_id}' not found.")
    return strat


@router.patch("/career-strategies/{strategy_id}", response_model=CareerStrategy)
async def update_career_strategy(
    strategy_id: str,
    request: CareerStrategyUpdateRequest,
    auth: AuthDep,
) -> CareerStrategy:
    """Updates configuration of an existing career strategy."""
    try:
        return recruitment_policy_service.update_strategy(strategy_id, request, auth_context=auth)
    except StrategyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.delete("/career-strategies/{strategy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_career_strategy(
    strategy_id: str,
    auth: AuthDep,
) -> None:
    """Deletes a career strategy."""
    success = recruitment_policy_service.delete_strategy(strategy_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Strategy '{strategy_id}' not found.")


@router.post("/career-strategies/{strategy_id}/activate", response_model=CareerStrategy)
async def activate_career_strategy(
    strategy_id: str,
    auth: AuthDep,
) -> CareerStrategy:
    """Activates a career strategy, making it the authoritative policy for future recruitment workflows."""
    try:
        return recruitment_policy_service.activate_strategy(strategy_id)
    except StrategyNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message)


@router.get("/career-strategies/{strategy_id}/versions", response_model=list[PolicyVersionSnapshot])
async def get_strategy_version_history(
    strategy_id: str,
    auth: AuthDep,
) -> list[PolicyVersionSnapshot]:
    """Retrieves immutable audit snapshot history for a career strategy."""
    return recruitment_policy_service.version_manager.get_version_history(strategy_id)


@router.get("/career-profiles/{profile_id}", response_model=CareerPreferenceProfile)
async def get_career_preference_profile(
    profile_id: str,
    auth: AuthDep,
) -> CareerPreferenceProfile:
    """Retrieves the unified career preference profile."""
    prof = recruitment_policy_service.get_career_profile(profile_id)
    if not prof:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Career profile '{profile_id}' not found.")
    return prof


# =============================================================================
# Policy Evaluation & Simulation
# =============================================================================

@router.post("/evaluate/job", response_model=RecruitmentDecision)
async def evaluate_job_policy(
    request: JobPolicyEvaluationRequest,
    auth: AuthDep,
) -> RecruitmentDecision:
    """Evaluates candidate eligibility and career policy rules against a job opportunity."""
    try:
        return await recruitment_policy_service.evaluate_job(
            job=request.job,
            strategy_id=request.strategy_id,
            profile_id=request.profile_id,
        )
    except RecruitmentPolicyError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.post("/policies/simulate", response_model=PolicySimulationResponse)
async def simulate_recruitment_policy(
    request: PolicySimulationRequest,
    auth: AuthDep,
) -> PolicySimulationResponse:
    """Executes a zero-side-effect policy simulation against a synthetic job opportunity."""
    try:
        return recruitment_policy_service.simulate_policy(request)
    except RecruitmentPolicyError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message)


@router.get("/policies/conflicts", response_model=list[PolicyConflictItem])
async def detect_policy_conflicts(
    auth: AuthDep,
    strategy_id: Optional[str] = Query(None),
) -> list[PolicyConflictItem]:
    """Scans the active or specified career strategy for contradictory rules."""
    strat = recruitment_policy_service.get_strategy(strategy_id) if strategy_id else recruitment_policy_service.get_active_strategy()
    if not strat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No active strategy found.")
    return PolicyRulesEngine.detect_conflicts(strat)


# =============================================================================
# Autonomy Modes & Standing Grants
# =============================================================================

@router.get("/autonomy/status")
async def get_autonomy_status(
    auth: AuthDep,
) -> dict:
    """Returns active autonomy mode, operational capabilities, and Emergency Stop state."""
    strategy = recruitment_policy_service.get_active_strategy()
    mode = strategy.autonomy_mode.value if strategy else "research_only"
    budget = recruitment_policy_service.budget_controller.get_budget()
    emergency_active = recruitment_policy_service.is_emergency_stop_active()

    return {
        "active_autonomy_mode": mode,
        "is_emergency_stop_active": emergency_active,
        "capabilities": {
            "can_discover_jobs": not emergency_active,
            "can_analyze_job_descriptions": not emergency_active,
            "can_prepare_resumes": not emergency_active and mode in ("prepare_and_review", "preauthorized_preparation", "bounded_autonomous_applications"),
            "can_prepare_answers": not emergency_active and mode in ("prepare_and_review", "preauthorized_preparation", "bounded_autonomous_applications"),
            "can_auto_submit": not emergency_active and mode == "bounded_autonomous_applications",
        },
        "remaining_daily_budget": budget.remaining_daily,
        "remaining_weekly_budget": budget.remaining_weekly,
        "grants_count": len(recruitment_policy_service.autonomy_controller.get_grants()),
    }


@router.get("/autonomy/grants", response_model=list[StandingGrantRecord])
async def list_standing_grants(
    auth: AuthDep,
) -> list[StandingGrantRecord]:
    """Lists all standing grants for recruitment automation."""
    return recruitment_policy_service.autonomy_controller.get_grants()


@router.post("/autonomy/grants", response_model=StandingGrantRecord, status_code=status.HTTP_201_CREATED)
async def create_standing_grant(
    auth: AuthDep,
    grantee_agent: str,
    action_type: str = "recruitment.application.prepare",
    max_operations: int = 50,
    validity_days: int = 30,
) -> StandingGrantRecord:
    """Creates a new bounded standing grant for an authorized specialist agent."""
    return recruitment_policy_service.autonomy_controller.create_grant(
        grantee_agent=grantee_agent,
        action_type=action_type,
        max_operations=max_operations,
        validity_days=validity_days,
    )


@router.post("/autonomy/grants/{grant_id}/revoke", response_model=dict)
async def revoke_standing_grant(
    grant_id: str,
    auth: AuthDep,
) -> dict:
    """Revokes a standing grant immediately, preventing further autonomous action execution."""
    success = recruitment_policy_service.autonomy_controller.revoke_grant(grant_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Grant '{grant_id}' not found.")
    return {"grant_id": grant_id, "status": "revoked"}


# =============================================================================
# Budgets & Multi-Agent Quotas
# =============================================================================

@router.get("/budgets", response_model=RecruitmentBudget)
async def get_recruitment_budget(
    auth: AuthDep,
) -> RecruitmentBudget:
    """Returns application quantity budgets, current reservations, and remaining limits."""
    return recruitment_policy_service.budget_controller.get_budget()


@router.put("/budgets", response_model=RecruitmentBudget)
async def update_recruitment_budget(
    budget: RecruitmentBudget,
    auth: AuthDep,
) -> RecruitmentBudget:
    """Updates recruitment application volume quotas."""
    recruitment_policy_service.budget_controller.set_budget(budget)
    return budget


@router.post("/budgets/reserve", response_model=BudgetReservationResponse)
async def reserve_budget_slot(
    request: BudgetReservationRequest,
    auth: AuthDep,
) -> BudgetReservationResponse:
    """Atomically reserves an application slot across concurrent agent workers."""
    return await recruitment_policy_service.budget_controller.reserve_budget(request)


@router.post("/budgets/confirm", response_model=dict)
async def confirm_budget_slot(
    reservation_id: str,
    auth: AuthDep,
) -> dict:
    """Confirms completion of an application operation and records confirmed usage."""
    success = await recruitment_policy_service.budget_controller.confirm_reservation(reservation_id)
    return {"reservation_id": reservation_id, "confirmed": success}


@router.post("/budgets/release", response_model=dict)
async def release_budget_slot(
    reservation_id: str,
    auth: AuthDep,
) -> dict:
    """Safely releases a pending reservation on workflow cancellation without deducting quota."""
    success = await recruitment_policy_service.budget_controller.release_reservation(reservation_id)
    return {"reservation_id": reservation_id, "released": success}


# =============================================================================
# Review Queue & Decisions Log
# =============================================================================

@router.get("/review-queue", response_model=list[ReviewQueueItem])
async def list_review_queue(
    auth: AuthDep,
    status_filter: Optional[str] = Query(None, alias="status"),
) -> list[ReviewQueueItem]:
    """Lists items in the human review queue."""
    return recruitment_policy_service.autonomy_controller.get_review_queue(status=status_filter)


@router.post("/review-queue/{item_id}/resolve", response_model=ReviewQueueItem)
async def resolve_review_queue_item(
    item_id: str,
    req: ReviewResolutionRequest,
    auth: AuthDep,
) -> ReviewQueueItem:
    """Resolves an escalated review item."""
    resolved = recruitment_policy_service.autonomy_controller.resolve_review_item(
        item_id, status=req.status, notes=req.notes
    )
    if not resolved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Review item '{item_id}' not found.")
    return resolved


@router.get("/policy-decisions", response_model=list[RecruitmentDecision])
async def list_policy_decisions(
    auth: AuthDep,
    limit: int = Query(50, ge=1, le=200),
) -> list[RecruitmentDecision]:
    """Retrieves recent recruitment policy decisions log."""
    return recruitment_policy_service.get_decisions_log(limit=limit)


@router.get("/policy-decisions/{decision_id}", response_model=RecruitmentDecision)
async def get_policy_decision(
    decision_id: str,
    auth: AuthDep,
) -> RecruitmentDecision:
    """Retrieves specific decision details and explanation report."""
    dec = recruitment_policy_service.get_decision(decision_id)
    if not dec:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Decision '{decision_id}' not found.")
    return dec


@router.get("/policy-diagnostics")
async def get_policy_diagnostics(
    auth: AuthDep,
) -> dict:
    """Returns engine diagnostics, active strategy, conflicts count, and system health."""
    strat = recruitment_policy_service.get_active_strategy()
    conflicts = PolicyRulesEngine.detect_conflicts(strat) if strat else []
    budget = recruitment_policy_service.budget_controller.get_budget()

    return {
        "status": "healthy",
        "active_strategy_id": strat.id if strat else None,
        "active_strategy_title": strat.title if strat else None,
        "conflicts_count": len(conflicts),
        "conflicts": [c.model_dump() for c in conflicts],
        "total_strategies": len(recruitment_policy_service.list_strategies()),
        "budget_remaining_daily": budget.remaining_daily,
        "budget_remaining_weekly": budget.remaining_weekly,
        "emergency_stop_engaged": recruitment_policy_service.is_emergency_stop_active(),
        "deterministic_rules_count": 14,
    }
