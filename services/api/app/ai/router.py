"""Intelligent Model Router evaluating task categories, capabilities, budgets, and privacy."""

import logging

from app.ai.contracts import (
    InferenceRequest,
    RoutingDecision,
    RoutingStrategy,
    TaskCategory,
)
from app.ai.errors import ModelNotFoundError, ProviderUnavailableError
from app.ai.registry import ProviderRegistry

logger = logging.getLogger("autonom.ai.router")

# Default preferred models per task category
CATEGORY_DEFAULT_PREFERENCES: dict[TaskCategory, dict[str, str]] = {
    TaskCategory.GENERAL_CONVERSATION: {"local": "llama3.1:8b", "cloud": "gpt-4o-mini"},
    TaskCategory.SHORT_REASONING: {"local": "llama3.1:8b", "cloud": "gpt-4o-mini"},
    TaskCategory.COMPLEX_REASONING: {"local": "llama3.1:8b", "cloud": "o1-mini"},
    TaskCategory.CODING: {"local": "llama3.1:8b", "cloud": "gpt-4o"},
    TaskCategory.CODE_REVIEW: {"local": "llama3.1:8b", "cloud": "gpt-4o"},
    TaskCategory.RESEARCH_SYNTHESIS: {"local": "llama3.1:8b", "cloud": "gpt-4o"},
    TaskCategory.DOCUMENT_WRITING: {"local": "llama3.1:8b", "cloud": "gpt-4o"},
    TaskCategory.JOB_DESCRIPTION_ANALYSIS: {"local": "llama3.1:8b", "cloud": "gpt-4o-mini"},
    TaskCategory.RESUME_ANALYSIS: {"local": "llama3.1:8b", "cloud": "gpt-4o"},
    TaskCategory.SCREENING_ANSWER_DRAFTING: {"local": "llama3.1:8b", "cloud": "gpt-4o-mini"},
    TaskCategory.SUMMARIZATION: {"local": "llama3.1:8b", "cloud": "gpt-4o-mini"},
    TaskCategory.STRUCTURED_EXTRACTION: {"local": "llama3.1:8b", "cloud": "gpt-4o-mini"},
    TaskCategory.CLASSIFICATION: {"local": "llama3.1:8b", "cloud": "gpt-4o-mini"},
    TaskCategory.PLANNING: {"local": "llama3.1:8b", "cloud": "gpt-4o"},
    TaskCategory.VISION_INTERPRETATION: {"local": "llava:7b", "cloud": "gpt-4o"},
    TaskCategory.COMPUTER_CONTROL_GROUNDING: {"local": "llama3.1:8b", "cloud": "gpt-4o"},
}


class IntelligentModelRouter:
    """Evaluates inference requests and deterministically selects the optimal provider/model."""

    def __init__(self, registry: ProviderRegistry) -> None:
        self.registry = registry

    def select_model(self, request: InferenceRequest) -> RoutingDecision:
        """Determines the best provider and model according to strategy, task category, and privacy policies."""
        # 1. Manual Strategy or explicit user selection
        if request.routing_strategy == RoutingStrategy.MANUAL:
            if not request.provider_preference or not request.model_preference:
                raise ModelNotFoundError(
                    "manual_selection_missing", "Manual routing requires provider & model preferences."
                )
            return RoutingDecision(
                selected_provider_id=request.provider_preference,
                selected_model_id=request.model_preference,
                strategy_used=RoutingStrategy.MANUAL,
                rule_applied="User Manual Override",
                explanation=f"User explicitly requested {request.provider_preference}:{request.model_preference}.",
                candidates_considered=[f"{request.provider_preference}:{request.model_preference}"],
                fallbacks_available=[],
                is_local=(request.provider_preference == "ollama"),
            )

        # 2. Strict Privacy Restriction: Local Only
        is_privacy_locked = request.is_local_only or (request.routing_strategy == RoutingStrategy.PRIVACY_RESTRICTED)

        # Gather discovered models from registry
        models = self.registry.list_models()
        local_models = [m for m in models if m.provider_type == "local" and m.is_available]
        cloud_models = [m for m in models if m.provider_type == "cloud" and m.is_available]

        # Filter by required capabilities if any
        if request.required_capabilities:
            req_caps = set(request.required_capabilities)
            local_models = [m for m in local_models if req_caps.issubset(set(m.capabilities))]
            cloud_models = [m for m in cloud_models if req_caps.issubset(set(m.capabilities))]

        # Filter by context budget
        local_models = [m for m in local_models if m.context_window >= min(request.context_budget, 4096)]
        cloud_models = [m for m in cloud_models if m.context_window >= request.context_budget]

        # 3. Privacy Restricted Strategy
        if is_privacy_locked:
            if not local_models:
                raise ProviderUnavailableError(
                    "ollama",
                    "Task is marked local-only or privacy-restricted, but no eligible local models are installed.",
                )
            selected = local_models[0]
            fallbacks = [m.id for m in local_models[1:]]
            return RoutingDecision(
                selected_provider_id=selected.provider_id,
                selected_model_id=selected.model_id,
                strategy_used=RoutingStrategy.PRIVACY_RESTRICTED,
                rule_applied="Local Privacy Boundary",
                explanation="Selected local model to guarantee zero cloud data transmission for sensitive content.",
                candidates_considered=[m.id for m in local_models],
                fallbacks_available=fallbacks,
                is_local=True,
            )

        # 4. Local First Strategy
        if request.routing_strategy in (RoutingStrategy.LOCAL_FIRST, RoutingStrategy.LOWEST_COST):
            if local_models:
                selected = local_models[0]
                fallbacks = [m.id for m in local_models[1:]] + (
                    [m.id for m in cloud_models] if request.allow_cloud_fallback else []
                )
                return RoutingDecision(
                    selected_provider_id=selected.provider_id,
                    selected_model_id=selected.model_id,
                    strategy_used=request.routing_strategy,
                    rule_applied="Local First Availability",
                    explanation=f"Selected installed local model '{selected.model_id}' with $0.00 cost.",
                    candidates_considered=[m.id for m in local_models + cloud_models],
                    fallbacks_available=fallbacks,
                    is_local=True,
                )
            # If no local models installed, evaluate cloud fallback if permitted
            if request.allow_cloud_fallback and cloud_models:
                selected = cloud_models[0]
                fallbacks = [m.id for m in cloud_models[1:]]
                return RoutingDecision(
                    selected_provider_id=selected.provider_id,
                    selected_model_id=selected.model_id,
                    strategy_used=request.routing_strategy,
                    rule_applied="Cloud Fallback (No Local Models Installed)",
                    explanation="No local models were installed or available; fell back to configured cloud model.",
                    candidates_considered=[m.id for m in cloud_models],
                    fallbacks_available=fallbacks,
                    is_local=False,
                )

        # 5. Cloud First Strategy
        if request.routing_strategy in (RoutingStrategy.CLOUD_FIRST, RoutingStrategy.CAPABILITY_FIRST):
            if cloud_models:
                selected = cloud_models[0]
                fallbacks = [m.id for m in cloud_models[1:]] + [m.id for m in local_models]
                return RoutingDecision(
                    selected_provider_id=selected.provider_id,
                    selected_model_id=selected.model_id,
                    strategy_used=request.routing_strategy,
                    rule_applied="Cloud First Preference",
                    explanation=f"Selected cloud model '{selected.display_name}' for highest performance.",
                    candidates_considered=[m.id for m in cloud_models + local_models],
                    fallbacks_available=fallbacks,
                    is_local=False,
                )
            if local_models:
                selected = local_models[0]
                return RoutingDecision(
                    selected_provider_id=selected.provider_id,
                    selected_model_id=selected.model_id,
                    strategy_used=request.routing_strategy,
                    rule_applied="Local Fallback (Cloud Unavailable)",
                    explanation="Cloud provider unavailable; fell back to local model.",
                    candidates_considered=[m.id for m in local_models],
                    fallbacks_available=[m.id for m in local_models[1:]],
                    is_local=True,
                )

        # Default fallback
        if local_models:
            sel = local_models[0]
            return RoutingDecision(
                selected_provider_id=sel.provider_id,
                selected_model_id=sel.model_id,
                strategy_used=RoutingStrategy.LOCAL_FIRST,
                rule_applied="Default Policy",
                explanation=f"Routed to local model '{sel.model_id}'.",
                is_local=True,
            )
        if cloud_models:
            sel = cloud_models[0]
            return RoutingDecision(
                selected_provider_id=sel.provider_id,
                selected_model_id=sel.model_id,
                strategy_used=RoutingStrategy.CLOUD_FIRST,
                rule_applied="Default Cloud Policy",
                explanation=f"Routed to cloud model '{sel.model_id}'.",
                is_local=False,
            )

        # When no models are installed or configured, provide explainable category expectation
        cat_pref = CATEGORY_DEFAULT_PREFERENCES.get(
            request.task_category, {"local": "llama3.1:8b", "cloud": "gpt-4o"}
        )
        is_loc = request.routing_strategy in (
            RoutingStrategy.LOCAL_FIRST,
            RoutingStrategy.PRIVACY_RESTRICTED,
            RoutingStrategy.LOWEST_COST,
        )
        target_prov = "ollama" if is_loc else "openai"
        target_model = cat_pref["local"] if is_loc else cat_pref["cloud"]

        return RoutingDecision(
            selected_provider_id=target_prov,
            selected_model_id=target_model,
            strategy_used=request.routing_strategy,
            rule_applied="Category Default (Awaiting Model Installation)",
            explanation=(
                f"Configured policy targets {target_prov}:{target_model} for {request.task_category.value}, "
                "but no models are currently installed or configured."
            ),
            candidates_considered=[],
            fallbacks_available=[],
            is_local=is_loc,
        )

    def resolve_fallback(
        self,
        request: InferenceRequest,
        failed_provider_id: str,
        failed_model_id: str,
    ) -> RoutingDecision | None:
        """Finds next eligible model excluding the failed provider/model."""
        if request.is_local_only or request.routing_strategy == RoutingStrategy.PRIVACY_RESTRICTED:
            # Privacy boundary: local alternatives only
            candidates = [
                m for m in self.registry.list_models("ollama") if m.is_available and m.model_id != failed_model_id
            ]
            if candidates:
                sel = candidates[0]
                return RoutingDecision(
                    selected_provider_id=sel.provider_id,
                    selected_model_id=sel.model_id,
                    strategy_used=RoutingStrategy.PRIVACY_RESTRICTED,
                    rule_applied="Local-Only Fallback",
                    explanation=f"Failed on {failed_provider_id}:{failed_model_id}; recovered to alternative local model '{sel.model_id}'.",
                    is_local=True,
                )
            return None

        # General fallback: check remaining models
        models = self.registry.list_models()
        candidates = [
            m
            for m in models
            if m.is_available and not (m.provider_id == failed_provider_id and m.model_id == failed_model_id)
        ]
        if not candidates:
            return None

        sel = candidates[0]
        return RoutingDecision(
            selected_provider_id=sel.provider_id,
            selected_model_id=sel.model_id,
            strategy_used=request.routing_strategy,
            rule_applied="Dynamic Error Fallback",
            explanation=f"Recovered from {failed_provider_id}:{failed_model_id} failure using {sel.id}.",
            is_local=(sel.provider_type == "local"),
        )
