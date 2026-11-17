"""FastAPI REST and SSE endpoints for the unified AI Model Gateway."""

import logging
from typing import Any

from fastapi import APIRouter, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field

from app.ai.contracts import (
    ChatMessage,
    HardwareTelemetry,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    ProviderHealth,
    RoutingDecision,
    RoutingStrategy,
    TaskCategory,
)
from app.ai.errors import (
    AIGatewayError,
    AuthenticationError,
    ContextLimitExceededError,
    ModelNotFoundError,
    RateLimitError,
)
from app.ai.factory import get_ai_gateway, set_cached_api_key
from app.api.dependencies import AuthDep
from app.db.engine import get_db_session
from app.repositories.ai_repository import AIRepository
from app.repositories.credential_repository import CredentialRepository

logger = logging.getLogger("autonom.api.ai")
router = APIRouter(prefix="/ai", tags=["AI Model Gateway"])


# ---------------------------------------------------------------------------
# Request Schemas
# ---------------------------------------------------------------------------
class ChatStreamPayload(BaseModel):
    prompt: str = Field(..., min_length=1)
    system_prompt: str | None = None
    messages: list[ChatMessage] = Field(default_factory=list)
    task_category: TaskCategory = TaskCategory.GENERAL_CONVERSATION
    routing_strategy: RoutingStrategy = RoutingStrategy.LOCAL_FIRST
    provider_preference: str | None = None
    model_preference: str | None = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=4096, ge=1, le=128000)
    is_local_only: bool = False
    allow_cloud_fallback: bool = True
    response_format: str = "text"
    json_schema: dict[str, Any] | None = None


class ModelLifecycleAction(BaseModel):
    model_id: str = Field(..., min_length=1)


class RoutingPreferenceUpdate(BaseModel):
    category: TaskCategory
    preferred_provider: str
    preferred_model: str
    fallback_provider: str | None = None
    fallback_model: str | None = None
    is_local_only: bool = False


# ---------------------------------------------------------------------------
# Helper: Synchronize API Keys from DPAPI Vault into Memory Cache
# ---------------------------------------------------------------------------
async def _sync_vault_credentials() -> None:
    try:
        async with get_db_session() as session:
            cred_repo = CredentialRepository(session)
            openai_key = await cred_repo.get_secret("openai")
            if openai_key:
                set_cached_api_key("openai", openai_key)
    except Exception as exc:
        logger.debug(f"Vault sync error: {exc}")


# ---------------------------------------------------------------------------
# 1. Provider & Discovery Endpoints
# ---------------------------------------------------------------------------
@router.get("/providers", response_model=list[dict[str, Any]])
async def list_providers(_auth: AuthDep) -> list[dict[str, Any]]:
    """Lists registered AI inference providers and their current status."""
    gateway = get_ai_gateway()
    return gateway.registry.list_providers()


@router.get("/providers/{provider_id}/health", response_model=ProviderHealth)
async def get_provider_health(
    provider_id: str,
    _auth: AuthDep,
) -> ProviderHealth:
    """Performs an active health and connectivity check against specified provider."""
    await _sync_vault_credentials()
    gateway = get_ai_gateway()
    try:
        provider = gateway.registry.get(provider_id)
        return await provider.health()
    except AIGatewayError as exc:
        return ProviderHealth(
            provider_id=provider_id,
            is_healthy=False,
            status="unavailable",
            error_message=exc.message,
        )


@router.get("/models", response_model=list[ModelInfo])
async def list_models(
    _auth: AuthDep,
    provider_id: str | None = None,
) -> list[ModelInfo]:
    """Returns list of all discovered and registered AI models."""
    gateway = get_ai_gateway()
    models = gateway.registry.list_models(provider_id=provider_id)
    if not models:
        # Trigger initial discovery
        models = await gateway.registry.discover_all_models()
    return models


@router.get("/models/{provider_id}/{model_id:path}", response_model=ModelInfo)
async def get_model(
    provider_id: str,
    model_id: str,
    _auth: AuthDep,
) -> ModelInfo:
    """Returns metadata for a specific provider model."""
    gateway = get_ai_gateway()
    model = gateway.registry.get_model(provider_id, model_id)
    if not model:
        try:
            provider = gateway.registry.get(provider_id)
            return await provider.get_model(model_id)
        except Exception as exc:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Model '{model_id}' not found on provider '{provider_id}': {exc}",
            ) from exc
    return model


@router.post("/models/refresh", response_model=list[ModelInfo])
async def refresh_models(
    _auth: AuthDep,
) -> list[ModelInfo]:
    """Triggers active model discovery across all providers and updates database cache."""
    await _sync_vault_credentials()
    gateway = get_ai_gateway()
    models = await gateway.registry.discover_all_models()

    # Persist into SQLite ai_models table
    try:
        async with get_db_session() as session:
            ai_repo = AIRepository(session)
            models_data = [
                {
                    "id": m.id,
                    "provider_id": m.provider_id,
                    "model_id": m.model_id,
                    "display_name": m.display_name,
                    "provider_type": m.provider_type,
                    "is_available": m.is_available,
                    "context_window": m.context_window,
                    "max_output_tokens": m.max_output_tokens,
                    "capabilities_json": m.capabilities,
                    "pricing_json": m.pricing.model_dump(),
                    "reported_size_bytes": m.reported_size_bytes,
                    "quantization": m.quantization,
                    "status_message": m.status_message,
                }
                for m in models
            ]
            await ai_repo.upsert_models(models_data)
    except Exception as exc:
        logger.warning(f"Error persisting refreshed models to database: {exc}")

    return models


# ---------------------------------------------------------------------------
# 2. Local Model Management (Load / Unload)
# ---------------------------------------------------------------------------
@router.post("/models/local/load", response_model=dict[str, Any])
async def load_local_model(
    payload: ModelLifecycleAction,
    _auth: AuthDep,
) -> dict[str, Any]:
    """Explicitly loads a local model into memory/VRAM according to single-active-model policy."""
    gateway = get_ai_gateway()
    try:
        ollama = gateway.registry.get("ollama")
        await gateway.resource_controller.ensure_model_ready(
            target_model_id=payload.model_id,
            provider_unload_fn=ollama.unload_model,
            provider_load_fn=ollama.load_model,
        )
        return {
            "status": "loaded",
            "model_id": payload.model_id,
            "currently_loaded": gateway.resource_controller.currently_loaded_model,
        }
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to load local model '{payload.model_id}': {exc}",
        ) from exc


@router.post("/models/local/unload", response_model=dict[str, Any])
async def unload_local_model(
    payload: ModelLifecycleAction,
    _auth: AuthDep,
) -> dict[str, Any]:
    """Unloads a local model to free VRAM."""
    gateway = get_ai_gateway()
    try:
        ollama = gateway.registry.get("ollama")
        success = await ollama.unload_model(payload.model_id)
        if payload.model_id == gateway.resource_controller.currently_loaded_model:
            gateway.resource_controller.set_loaded_model(None)
        return {"status": "unloaded" if success else "failed", "model_id": payload.model_id}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to unload model '{payload.model_id}': {exc}",
        ) from exc


# ---------------------------------------------------------------------------
# 3. Inference & Streaming Endpoints
# ---------------------------------------------------------------------------
@router.post("/requests", response_model=InferenceResponse)
async def create_inference_request(
    request: InferenceRequest,
    _auth: AuthDep,
) -> InferenceResponse:
    """Executes complete non-streaming inference with routing, fallback, and audit logging."""
    await _sync_vault_credentials()
    gateway = get_ai_gateway()

    try:
        if request.response_format in ("json_object", "json_schema"):
            response = await gateway.generate_structured(request, target_schema=request.json_schema)
        else:
            response = await gateway.generate(request)

        # Log into SQLite
        try:
            async with get_db_session() as session:
                ai_repo = AIRepository(session)
                await ai_repo.record_request(
                    request_id=response.request_id,
                    task_id=request.task_id,
                    task_category=request.task_category.value,
                    provider_id=response.provider_id,
                    model_id=response.model_id,
                    routing_strategy=request.routing_strategy.value,
                    status="completed",
                    prompt_tokens=response.usage.prompt_tokens,
                    completion_tokens=response.usage.completion_tokens,
                    total_tokens=response.usage.total_tokens,
                    tokens_source=response.usage.source,
                    estimated_cost_usd=response.estimated_cost_usd,
                    latency_ms=response.latency_ms,
                    routing_decision_json=response.routing_decision.model_dump() if response.routing_decision else {},
                    prompt_preview=(request.messages[-1].content[:200] if request.messages else None),
                )
        except Exception as exc:
            logger.warning(f"Error persisting inference request to SQLite: {exc}")

        return response

    except AuthenticationError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=exc.message) from exc
    except ModelNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=exc.message) from exc
    except ContextLimitExceededError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=exc.message) from exc
    except RateLimitError as exc:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail=exc.message) from exc
    except AIGatewayError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=exc.message) from exc


@router.post("/chat/stream")
async def stream_chat_inference(
    payload: ChatStreamPayload,
    _auth: AuthDep,
) -> StreamingResponse:
    """Provides real-time SSE streaming of token chunks with lifecycle start/complete frames."""
    await _sync_vault_credentials()
    gateway = get_ai_gateway()

    messages = list(payload.messages)
    if payload.prompt and (not messages or messages[-1].content != payload.prompt):
        messages.append(ChatMessage(role="user", content=payload.prompt))

    req = InferenceRequest(
        task_category=payload.task_category,
        routing_strategy=payload.routing_strategy,
        messages=messages,
        system_prompt=payload.system_prompt,
        provider_preference=payload.provider_preference,
        model_preference=payload.model_preference,
        temperature=payload.temperature,
        top_p=payload.top_p,
        max_tokens=payload.max_tokens,
        is_local_only=payload.is_local_only,
        allow_cloud_fallback=payload.allow_cloud_fallback,
        stream=True,
    )

    return StreamingResponse(
        gateway.stream(req),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/requests/{request_id}/cancel", response_model=dict[str, Any])
async def cancel_inference_request(
    request_id: str,
    _auth: AuthDep,
) -> dict[str, Any]:
    """Cancels an active generation stream or worker execution."""
    gateway = get_ai_gateway()
    success = gateway.cancel(request_id)
    return {"request_id": request_id, "cancelled": success}


@router.post("/route/preview", response_model=RoutingDecision)
async def preview_routing_decision(
    request: InferenceRequest,
    _auth: AuthDep,
) -> RoutingDecision:
    """Pre-evaluates routing logic and returns an explainable decision without invoking models."""
    gateway = get_ai_gateway()
    try:
        return await gateway.preview_route(request)
    except AIGatewayError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=exc.message) from exc


# ---------------------------------------------------------------------------
# 4. Telemetry, Usage Analytics & Hardware
# ---------------------------------------------------------------------------
@router.get("/resources", response_model=HardwareTelemetry)
async def get_hardware_resources(
    _auth: AuthDep,
) -> HardwareTelemetry:
    """Returns live hardware telemetry: system RAM and NVIDIA RTX 4050 GPU VRAM metrics."""
    gateway = get_ai_gateway()
    return gateway.get_hardware_telemetry()


@router.get("/usage", response_model=dict[str, Any])
async def get_ai_usage_summary(
    _auth: AuthDep,
    days: int = Query(30, ge=1, le=365),
) -> dict[str, Any]:
    """Returns aggregated token usage, cost history, and provider distributions."""
    async with get_db_session() as session:
        ai_repo = AIRepository(session)
        return await ai_repo.get_usage_summary(days=days)


@router.get("/requests", response_model=dict[str, Any])
async def list_inference_requests(
    _auth: AuthDep,
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    provider_id: str | None = None,
    status: str | None = None,
    category: str | None = None,
) -> dict[str, Any]:
    """Lists past inference requests with paged metadata."""
    async with get_db_session() as session:
        ai_repo = AIRepository(session)
        records, total = await ai_repo.list_requests(
            limit=limit,
            offset=offset,
            provider_id=provider_id,
            status=status,
            task_category=category,
        )
        items = [
            {
                "id": r.id,
                "task_id": r.task_id,
                "task_category": r.task_category,
                "provider_id": r.provider_id,
                "model_id": r.model_id,
                "status": r.status,
                "prompt_tokens": r.prompt_tokens,
                "completion_tokens": r.completion_tokens,
                "total_tokens": r.total_tokens,
                "estimated_cost_usd": r.estimated_cost_usd,
                "latency_ms": r.latency_ms,
                "routing_strategy": r.routing_strategy,
                "prompt_preview": r.prompt_preview,
                "created_at": r.created_at.isoformat(),
            }
            for r in records
        ]
        return {"items": items, "total": total, "limit": limit, "offset": offset}


# ---------------------------------------------------------------------------
# 5. Routing Preferences Endpoints
# ---------------------------------------------------------------------------
@router.get("/routing/preferences", response_model=list[dict[str, Any]])
async def get_routing_preferences(
    _auth: AuthDep,
) -> list[dict[str, Any]]:
    """Returns user routing preferences per task category."""
    async with get_db_session() as session:
        ai_repo = AIRepository(session)
        records = await ai_repo.get_routing_preferences()
        return [
            {
                "category": r.category,
                "preferred_provider": r.preferred_provider,
                "preferred_model": r.preferred_model,
                "fallback_provider": r.fallback_provider,
                "fallback_model": r.fallback_model,
                "is_local_only": r.is_local_only,
                "updated_at": r.updated_at.isoformat(),
            }
            for r in records
        ]


@router.patch("/routing/preferences", response_model=dict[str, Any])
async def update_routing_preference(
    payload: RoutingPreferenceUpdate,
    _auth: AuthDep,
) -> dict[str, Any]:
    """Updates routing preference for a specific task category."""
    async with get_db_session() as session:
        ai_repo = AIRepository(session)
        record = await ai_repo.upsert_routing_preference(
            category=payload.category.value,
            preferred_provider=payload.preferred_provider,
            preferred_model=payload.preferred_model,
            fallback_provider=payload.fallback_provider,
            fallback_model=payload.fallback_model,
            is_local_only=payload.is_local_only,
        )
        return {
            "category": record.category,
            "preferred_provider": record.preferred_provider,
            "preferred_model": record.preferred_model,
            "fallback_provider": record.fallback_provider,
            "fallback_model": record.fallback_model,
            "is_local_only": record.is_local_only,
            "status": "updated",
        }
