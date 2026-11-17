"""Comprehensive automated unit and integration tests for the AI Model Gateway."""

import json

import pytest
from httpx import AsyncClient

from app.ai.budgets import budget_manager
from app.ai.cancellation import cancellation_manager
from app.ai.context import context_manager
from app.ai.contracts import (
    ChatMessage,
    InferenceChunk,
    InferenceRequest,
    InferenceResponse,
    ModelInfo,
    ModelPricing,
    ProviderHealth,
    RoutingStrategy,
    TaskCategory,
    TokenUsage,
)
from app.ai.errors import (
    ContextLimitExceededError,
    ProviderUnavailableError,
)
from app.ai.providers.base import AIProvider
from app.ai.registry import ProviderRegistry
from app.ai.resources.controller import LocalModelResourceController
from app.ai.router import IntelligentModelRouter


# ---------------------------------------------------------------------------
# Test Double Provider for Mocking
# ---------------------------------------------------------------------------
class DummyTestProvider(AIProvider):
    def __init__(self, provider_id: str, display_name: str, provider_type: str = "cloud") -> None:
        super().__init__(provider_id, display_name, provider_type)
        self.unload_called_with = []

    async def health(self) -> ProviderHealth:
        return ProviderHealth(provider_id=self.provider_id, is_healthy=True, status="available", latency_ms=12.5)

    async def list_models(self) -> list[ModelInfo]:
        return [
            ModelInfo(
                id=f"{self.provider_id}:test-model",
                provider_id=self.provider_id,
                model_id="test-model",
                display_name="Test Model",
                provider_type=self.provider_type,  # type: ignore[arg-type]
                is_available=True,
                context_window=8192,
                max_output_tokens=4096,
                capabilities=["chat", "streaming", "structured_output"],
                pricing=ModelPricing(input_cost_per_million=1.0, output_cost_per_million=2.0),
            )
        ]

    async def get_model(self, model_id: str) -> ModelInfo:
        models = await self.list_models()
        return models[0]

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        content = "Simulated response content"
        structured_data = None
        if request.response_format in ("json_object", "json_schema"):
            structured_data = {"status": "success", "result": "parsed"}
            content = json.dumps(structured_data)

        return InferenceResponse(
            request_id=request.request_id,
            provider_id=self.provider_id,
            model_id=request.model_preference or "test-model",
            content=content,
            finish_reason="stop",
            usage=TokenUsage(prompt_tokens=15, completion_tokens=8, total_tokens=23, source="reported"),
            estimated_cost_usd=0.0001,
            latency_ms=45.0,
            structured_data=structured_data,
        )

    async def stream(self, request: InferenceRequest):
        for token in ["Hello", " ", "from", " ", "test"]:
            yield InferenceChunk(
                request_id=request.request_id,
                provider_id=self.provider_id,
                model_id="test-model",
                delta=token,
            )
        yield InferenceChunk(
            request_id=request.request_id,
            provider_id=self.provider_id,
            model_id="test-model",
            finish_reason="stop",
            usage=TokenUsage(prompt_tokens=10, completion_tokens=5, total_tokens=15, source="reported"),
        )

    async def unload_model(self, model_id: str) -> bool:
        self.unload_called_with.append(model_id)
        return True


# ---------------------------------------------------------------------------
# 1. Budgets and Context Management Unit Tests
# ---------------------------------------------------------------------------
def test_budget_manager_cost_calculations():
    # Local is free
    cost_local = budget_manager.calculate_cost("ollama", "llama3.1:8b", 1000, 500)
    assert cost_local == 0.0

    # OpenAI GPT-4o pricing: $2.50 / $10.00
    cost_openai = budget_manager.calculate_cost("openai", "gpt-4o", 10_000, 5_000)
    # (10000/1e6)*2.50 = 0.025; (5000/1e6)*10.00 = 0.050 -> 0.075
    assert cost_openai == 0.075


def test_context_budget_manager_validation():
    messages = [
        ChatMessage(role="user", content="Hello world!"),
        ChatMessage(role="assistant", content="Hi, how can I assist you today?"),
    ]
    tokens = context_manager.count_messages_tokens(messages, system_prompt="You are helpful.")
    assert tokens > 0

    # Valid within 8k context
    valid_msgs, usage, was_truncated = context_manager.prepare_and_validate_context(
        messages=messages,
        system_prompt="System prompt",
        context_window=8192,
        max_output_tokens=1024,
        model_id="test-model",
        auto_truncate=False,
    )
    assert not was_truncated
    assert len(valid_msgs) == 2


def test_context_budget_manager_exceeded():
    messages = [ChatMessage(role="user", content="A" * 4000)]
    with pytest.raises(ContextLimitExceededError):
        context_manager.prepare_and_validate_context(
            messages=messages,
            system_prompt=None,
            context_window=500,  # Far too small
            max_output_tokens=256,
            model_id="small-model",
            auto_truncate=False,
        )


# ---------------------------------------------------------------------------
# 2. Router Unit Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_router_local_first_and_privacy_restriction():
    registry = ProviderRegistry()
    local_p = DummyTestProvider("ollama", "Ollama", "local")
    cloud_p = DummyTestProvider("openai", "OpenAI", "cloud")
    registry.register(local_p)
    registry.register(cloud_p)
    await registry.discover_all_models()

    router = IntelligentModelRouter(registry)

    # 1. Local First selects local
    req_local = InferenceRequest(
        task_category=TaskCategory.CODING,
        routing_strategy=RoutingStrategy.LOCAL_FIRST,
        messages=[ChatMessage(role="user", content="Write code")],
    )
    decision = router.select_model(req_local)
    assert decision.selected_provider_id == "ollama"
    assert decision.is_local is True

    # 2. Privacy restricted requires local
    req_privacy = InferenceRequest(
        is_local_only=True,
        messages=[ChatMessage(role="user", content="Confidential info")],
    )
    decision_priv = router.select_model(req_privacy)
    assert decision_priv.selected_provider_id == "ollama"
    assert decision_priv.is_local is True


@pytest.mark.asyncio
async def test_router_cloud_first_preference():
    registry = ProviderRegistry()
    local_p = DummyTestProvider("ollama", "Ollama", "local")
    cloud_p = DummyTestProvider("openai", "OpenAI", "cloud")
    registry.register(local_p)
    registry.register(cloud_p)
    await registry.discover_all_models()

    router = IntelligentModelRouter(registry)

    req_cloud = InferenceRequest(
        task_category=TaskCategory.RESEARCH_SYNTHESIS,
        routing_strategy=RoutingStrategy.CLOUD_FIRST,
        messages=[ChatMessage(role="user", content="Research summary")],
    )
    decision = router.select_model(req_cloud)
    assert decision.selected_provider_id == "openai"
    assert decision.is_local is False


def test_router_privacy_restricted_fails_when_no_local_model():
    registry = ProviderRegistry()
    cloud_p = DummyTestProvider("openai", "OpenAI", "cloud")
    registry.register(cloud_p)

    router = IntelligentModelRouter(registry)

    req_priv = InferenceRequest(is_local_only=True)
    with pytest.raises(ProviderUnavailableError) as exc_info:
        router.select_model(req_priv)
    assert "privacy-restricted" in str(exc_info.value).lower()


# ---------------------------------------------------------------------------
# 3. Resource Controller & Single Model Rule
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_resource_controller_single_active_model_switch():
    controller = LocalModelResourceController(max_concurrent_local=1)
    unloaded_models = []

    async def mock_unload(model_id: str):
        unloaded_models.append(model_id)
        return True

    # 1. Ensure model A ready
    await controller.ensure_model_ready("model-A", provider_unload_fn=mock_unload)
    assert controller.currently_loaded_model == "model-A"
    assert unloaded_models == []

    # 2. Switch to model B -> triggers unload of model A
    await controller.ensure_model_ready("model-B", provider_unload_fn=mock_unload)
    assert controller.currently_loaded_model == "model-B"
    assert unloaded_models == ["model-A"]


# ---------------------------------------------------------------------------
# 4. Cancellation Manager Test
# ---------------------------------------------------------------------------
def test_cancellation_manager_flow():
    req_id = "test-req-123"
    token = cancellation_manager.register(req_id)
    assert not cancellation_manager.is_cancelled(req_id)

    cancelled = cancellation_manager.cancel(req_id)
    assert cancelled is True
    assert cancellation_manager.is_cancelled(req_id)
    assert token.is_set()

    cancellation_manager.unregister(req_id)
    assert not cancellation_manager.is_cancelled(req_id)


# ---------------------------------------------------------------------------
# 5. Full Gateway Execution & Fallback Integration Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_gateway_generate_and_structured():
    registry = ProviderRegistry()
    provider = DummyTestProvider("ollama", "Ollama", "local")
    registry.register(provider)

    from app.ai.gateway import AIGateway

    gateway = AIGateway(registry=registry)

    req = InferenceRequest(
        task_category=TaskCategory.GENERAL_CONVERSATION,
        messages=[ChatMessage(role="user", content="Hello test")],
    )
    res = await gateway.generate(req)
    assert res.content == "Simulated response content"
    assert res.usage.total_tokens == 23

    # Test structured generation
    req_struct = InferenceRequest(
        task_category=TaskCategory.STRUCTURED_EXTRACTION,
        messages=[ChatMessage(role="user", content="Parse this")],
    )
    res_struct = await gateway.generate_structured(req_struct, target_schema={"type": "object"})
    assert res_struct.structured_data == {"status": "success", "result": "parsed"}


# ---------------------------------------------------------------------------
# 6. REST API Endpoints Integration Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_api_ai_endpoints_integration(async_client: AsyncClient, auth_headers: dict[str, str]):
    # 1. GET /api/v1/ai/providers
    res = await async_client.get("/api/v1/ai/providers", headers=auth_headers)
    assert res.status_code == 200
    providers = res.json()
    assert any(p["provider_id"] == "ollama" for p in providers)

    # 2. GET /api/v1/ai/resources (RTX 4050 / RAM telemetry)
    res_res = await async_client.get("/api/v1/ai/resources", headers=auth_headers)
    assert res_res.status_code == 200
    telemetry = res_res.json()
    assert "system_ram_total_mb" in telemetry
    assert "gpu_name" in telemetry

    # 3. POST /api/v1/ai/route/preview
    preview_req = {
        "task_category": "coding",
        "routing_strategy": "local_first",
        "messages": [{"role": "user", "content": "Write a python function"}],
    }
    res_preview = await async_client.post("/api/v1/ai/route/preview", json=preview_req, headers=auth_headers)
    assert res_preview.status_code == 200
    decision = res_preview.json()
    assert "selected_provider_id" in decision
    assert "rule_applied" in decision

    # 4. GET /api/v1/ai/usage
    res_usage = await async_client.get("/api/v1/ai/usage?days=7", headers=auth_headers)
    assert res_usage.status_code == 200
    usage_data = res_usage.json()
    assert "total_requests" in usage_data
    assert "success_rate_percent" in usage_data
