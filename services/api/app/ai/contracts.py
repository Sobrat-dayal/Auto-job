"""Strongly-typed contracts, schemas, and models for the unified AI Model Gateway."""

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any, Literal

from pydantic import BaseModel, Field


class TaskCategory(StrEnum):
    """16 discrete task categories for intelligent model routing."""

    GENERAL_CONVERSATION = "general_conversation"
    SHORT_REASONING = "short_reasoning"
    COMPLEX_REASONING = "complex_reasoning"
    CODING = "coding"
    CODE_REVIEW = "code_review"
    RESEARCH_SYNTHESIS = "research_synthesis"
    DOCUMENT_WRITING = "document_writing"
    JOB_DESCRIPTION_ANALYSIS = "job_description_analysis"
    RESUME_ANALYSIS = "resume_analysis"
    SCREENING_ANSWER_DRAFTING = "screening_answer_drafting"
    SUMMARIZATION = "summarization"
    STRUCTURED_EXTRACTION = "structured_extraction"
    CLASSIFICATION = "classification"
    PLANNING = "planning"
    VISION_INTERPRETATION = "vision_interpretation"
    COMPUTER_CONTROL_GROUNDING = "computer_control_grounding"


class RoutingStrategy(StrEnum):
    """Strategies for model selection."""

    LOCAL_FIRST = "local_first"
    CLOUD_FIRST = "cloud_first"
    LOWEST_COST = "lowest_cost"
    LOWEST_LATENCY = "lowest_latency"
    CAPABILITY_FIRST = "capability_first"
    MANUAL = "manual"
    PRIVACY_RESTRICTED = "privacy_restricted"


class ModelCapability(StrEnum):
    """Model capabilities for capability-based filtering."""

    CHAT = "chat"
    STREAMING = "streaming"
    STRUCTURED_OUTPUT = "structured_output"
    TOOL_CALLING = "tool_calling"
    VISION = "vision"
    EMBEDDINGS = "embeddings"
    REASONING = "reasoning"


class ChatMessage(BaseModel):
    """Single chat message in conversation history."""

    role: Literal["system", "user", "assistant", "tool"] = "user"
    content: str = ""
    name: str | None = None


class TokenUsage(BaseModel):
    """Token usage metrics."""

    prompt_tokens: int = 0
    completion_tokens: int = 0
    total_tokens: int = 0
    source: Literal["reported", "estimated", "unknown"] = "reported"


class ModelPricing(BaseModel):
    """Pricing rates per 1M tokens in USD."""

    input_cost_per_million: float = 0.0
    output_cost_per_million: float = 0.0


class ModelInfo(BaseModel):
    """Metadata describing a registered local or cloud model."""

    id: str  # provider_id:model_id
    provider_id: str
    model_id: str
    display_name: str
    provider_type: Literal["local", "cloud"] = "local"
    is_available: bool = True
    context_window: int = 8192
    max_output_tokens: int = 4096
    capabilities: list[str] = Field(default_factory=lambda: ["chat", "streaming"])
    pricing: ModelPricing = Field(default_factory=ModelPricing)
    reported_size_bytes: int | None = None
    quantization: str | None = None
    status_message: str | None = None
    last_discovered_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProviderHealth(BaseModel):
    """Provider connectivity and health state."""

    provider_id: str
    is_healthy: bool = False
    status: Literal["available", "unavailable", "degraded", "auth_required", "disabled"] = "unavailable"
    latency_ms: float | None = None
    error_message: str | None = None
    last_checked_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class RoutingDecision(BaseModel):
    """Explainable routing decision."""

    selected_provider_id: str
    selected_model_id: str
    strategy_used: RoutingStrategy
    rule_applied: str
    explanation: str
    candidates_considered: list[str] = Field(default_factory=list)
    fallbacks_available: list[str] = Field(default_factory=list)
    is_local: bool = True


class InferenceRequest(BaseModel):
    """Typed request for inference execution."""

    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    task_id: str | None = None
    task_category: TaskCategory = TaskCategory.GENERAL_CONVERSATION
    messages: list[ChatMessage] = Field(default_factory=list)
    system_prompt: str | None = None
    provider_preference: str | None = None
    model_preference: str | None = None
    routing_strategy: RoutingStrategy = RoutingStrategy.LOCAL_FIRST
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    top_p: float = Field(default=0.9, ge=0.0, le=1.0)
    max_tokens: int = Field(default=4096, ge=1, le=128000)
    context_budget: int = Field(default=8192, ge=512, le=128000)
    timeout_seconds: float = Field(default=60.0, ge=5.0, le=600.0)
    stream: bool = False
    response_format: Literal["text", "json_object", "json_schema"] = "text"
    json_schema: dict[str, Any] | None = None
    allow_cloud_fallback: bool = True
    is_local_only: bool = False
    max_cost_usd: float | None = None
    required_capabilities: list[str] = Field(default_factory=list)
    correlation_id: str | None = None


class InferenceResponse(BaseModel):
    """Normalized response envelope for complete inference generation."""

    request_id: str
    provider_id: str
    model_id: str
    content: str
    finish_reason: str | None = "stop"
    usage: TokenUsage = Field(default_factory=TokenUsage)
    estimated_cost_usd: float = 0.0
    latency_ms: float = 0.0
    time_to_first_token_ms: float | None = None
    routing_decision: RoutingDecision | None = None
    structured_data: Any | None = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class InferenceChunk(BaseModel):
    """Incremental chunk emitted during streaming token generation."""

    request_id: str
    provider_id: str
    model_id: str
    delta: str = ""
    finish_reason: str | None = None
    usage: TokenUsage | None = None


class HardwareTelemetry(BaseModel):
    """Host hardware resource telemetry snapshot."""

    system_ram_total_mb: int = 0
    system_ram_available_mb: int = 0
    system_ram_used_mb: int = 0
    system_ram_percent: float = 0.0
    gpu_name: str | None = None
    gpu_vram_total_mb: int | None = None
    gpu_vram_used_mb: int | None = None
    gpu_vram_available_mb: int | None = None
    gpu_vram_percent: float | None = None
    active_local_model: str | None = None
    active_inference_count: int = 0
    local_concurrency_limit: int = 1
    timestamp: datetime = Field(default_factory=lambda: datetime.now(UTC))
