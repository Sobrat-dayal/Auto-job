"""Deterministic policy evaluation and action risk classification."""

import logging
from typing import Any

from app.security.authorization.contracts import (
    ActionEffect,
    AuthorizationRequest,
    GrantDefinition,
    PermissionCategory,
    PolicyDefinition,
    RiskLevel,
)
from app.security.authorization.scopes import matches_resource_scope

logger = logging.getLogger("autonom.security.authorization.evaluator")

# Action risk mapping catalog
CAPABILITY_RISK_MAP: dict[str, RiskLevel] = {
    # Low Risk (Read-only, analysis, formatting)
    "recruitment_match_skills": RiskLevel.LOW,
    "recruitment_extract_job_requirements": RiskLevel.LOW,
    "recruitment_normalize_job_listing": RiskLevel.LOW,
    "recruitment_parse_search_criteria": RiskLevel.LOW,
    "recruitment_classify_application_fields": RiskLevel.LOW,
    "recruitment_summarize_conversation": RiskLevel.LOW,
    "recruitment_generate_interview_questions": RiskLevel.LOW,
    "code_explain": RiskLevel.LOW,
    "code_review_static": RiskLevel.LOW,
    "research_summarize_sources": RiskLevel.LOW,
    "research_extract_evidence": RiskLevel.LOW,
    "research_compare_sources": RiskLevel.LOW,
    "market_analyze_supplied_data": RiskLevel.LOW,
    "doc_generate_outline": RiskLevel.LOW,
    "sheet_summarize_tabular": RiskLevel.LOW,
    "sheet_explain_formula": RiskLevel.LOW,
    "pres_generate_outline": RiskLevel.LOW,
    "pres_draft_speaker_notes": RiskLevel.LOW,
    "msg_classify_message": RiskLevel.LOW,
    "visual_inspect_image_metadata": RiskLevel.LOW,
    "structural_parse_accessibility_tree": RiskLevel.LOW,
    "workflow_validate_config": RiskLevel.LOW,
    "text_summarize": RiskLevel.LOW,
    "text_classify": RiskLevel.LOW,
    "structured_extract": RiskLevel.LOW,
    "text_compare": RiskLevel.LOW,
    "output_validate": RiskLevel.LOW,
    "code_inspect": RiskLevel.LOW,
    # Moderate Risk (Drafting content, creating new files, non-destructive synthesis)
    "recruitment_draft_resume_bullets": RiskLevel.MODERATE,
    "recruitment_draft_recruiter_reply": RiskLevel.MODERATE,
    "code_generate_tests": RiskLevel.MODERATE,
    "doc_draft_report": RiskLevel.MODERATE,
    "doc_rewrite_text": RiskLevel.MODERATE,
    "creative_scene_specification": RiskLevel.MODERATE,
    "msg_draft_response": RiskLevel.MODERATE,
    "workflow_propose_template": RiskLevel.MODERATE,
    "browser_plan_navigation": RiskLevel.MODERATE,
    "desktop_plan_operation": RiskLevel.MODERATE,
    "data_transform": RiskLevel.MODERATE,
    # High Risk (External execution, live form filling, outbound network, file mutation)
    "browser_navigate": RiskLevel.HIGH,
    "browser_submit_form": RiskLevel.HIGH,
    "email_send": RiskLevel.HIGH,
    "recruitment_submit_application": RiskLevel.HIGH,
    "desktop_execute_command": RiskLevel.HIGH,
    "desktop_inject_input": RiskLevel.HIGH,
    "fs_modify_file": RiskLevel.HIGH,
    # Critical Risk (Destruction, credential extraction, security policy mutation)
    "fs_delete_file": RiskLevel.CRITICAL,
    "fs_delete_directory": RiskLevel.CRITICAL,
    "security_modify_policy": RiskLevel.CRITICAL,
    "credential_read_secret": RiskLevel.CRITICAL,
    "database_wipe_data": RiskLevel.CRITICAL,
    "database_restore_backup": RiskLevel.CRITICAL,
}


def classify_action_risk(capability_id: str, action: str = "") -> RiskLevel:
    """Deterministically classifies risk level based on capability and action identifier."""
    if capability_id in CAPABILITY_RISK_MAP:
        return CAPABILITY_RISK_MAP[capability_id]
    if action in CAPABILITY_RISK_MAP:
        return CAPABILITY_RISK_MAP[action]

    # Keyword heuristics
    action_lower = f"{capability_id}_{action}".lower()
    if any(k in action_lower for k in ("delete", "destroy", "wipe", "drop", "revoke", "purge")):
        return RiskLevel.CRITICAL
    if any(k in action_lower for k in ("submit", "send", "post", "execute", "inject", "transact", "modify")):
        return RiskLevel.HIGH
    if any(k in action_lower for k in ("write", "draft", "create", "generate", "transform", "update")):
        return RiskLevel.MODERATE

    return RiskLevel.LOW


def matches_subject_scope(subject_scope: str, request: AuthorizationRequest) -> bool:
    """Checks whether an agent or actor matches the policy's subject scope."""
    if subject_scope == "*":
        return True
    if subject_scope == "agent:*" and request.actor.agent_id:
        return True
    if subject_scope == "user:*" and request.actor.actor_type == "user":
        return True
    if request.actor.agent_id and subject_scope == request.actor.agent_id:
        return True
    if subject_scope == request.actor.actor_id:
        return True
    return False


def matches_action_scope(action_scope: list[str], request: AuthorizationRequest) -> bool:
    """Checks whether capability_id or action matches the action scope."""
    if not action_scope or "*" in action_scope:
        return True
    if request.capability_id in action_scope:
        return True
    if request.action in action_scope:
        return True
    return False


def evaluate_policy_rule(
    policy: PolicyDefinition,
    request: AuthorizationRequest,
    risk: RiskLevel,
) -> ActionEffect | None:
    """Evaluates a single policy definition against an authorization request.

    Returns ActionEffect if matched, or None if the policy does not apply.
    """
    if not policy.is_enabled:
        return None

    # Check subject scope
    if not matches_subject_scope(policy.subject_scope, request):
        return None

    # Check action scope
    if not matches_action_scope(policy.action_scope, request):
        return None

    # Check resource scope
    if not matches_resource_scope(request.resource_scope, policy.resource_scope):
        return None

    # Check risk constraint if defined in conditions
    max_risk_str = policy.conditions.get("max_risk_level")
    if max_risk_str:
        try:
            max_risk = RiskLevel(max_risk_str)
            if risk.level_order > max_risk.level_order:
                # If action risk exceeds policy max risk, force REQUIRE_APPROVAL
                logger.info(
                    "Action risk %s exceeds policy '%s' max risk %s: escalating to approval",
                    risk.value,
                    policy.id,
                    max_risk.value,
                )
                return ActionEffect.REQUIRE_APPROVAL
        except ValueError:
            pass

    return policy.effect


def evaluate_grant_match(grant: GrantDefinition, request: AuthorizationRequest) -> bool:
    """Checks whether an active authorization grant covers the request."""
    if not grant.is_active:
        return False

    # Workflow scope check
    if grant.grant_type == "workflow_scoped" and grant.workflow_id:
        if request.actor.workflow_id != grant.workflow_id:
            return False

    # Task scope check
    if grant.grant_type == "task_scoped" and grant.task_id:
        if request.actor.task_id != grant.task_id:
            return False

    # Subject check
    if grant.subject_id != "*":
        target = request.actor.agent_id or request.actor.actor_id
        if target != grant.subject_id:
            return False

    # Capability check
    if grant.allowed_capabilities and "*" not in grant.allowed_capabilities:
        if request.capability_id not in grant.allowed_capabilities and request.action not in grant.allowed_capabilities:
            return False

    # Resource scope check
    if not matches_resource_scope(request.resource_scope, grant.resource_scope):
        return False

    return True
