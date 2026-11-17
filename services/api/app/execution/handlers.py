"""TaskHandler base abstraction, HandlerRegistry, and built-in safe demonstration handlers."""

import asyncio
import json
from abc import ABC, abstractmethod
from typing import Any

from app.core.exceptions import TaskCancelledError, TaskExecutionError, UnknownTaskTypeError
from app.execution.context import TaskExecutionContext


class TaskHandler(ABC):
    """Abstract base class for all task execution handlers."""

    @abstractmethod
    async def execute(self, payload: dict[str, Any], context: TaskExecutionContext) -> Any:
        """Executes the task logic using provided input payload and execution context."""


class ComputeEchoHandler(TaskHandler):
    """Deterministic demonstration task handler that reverses/transforms input payload."""

    async def execute(self, payload: dict[str, Any], context: TaskExecutionContext) -> dict[str, Any]:
        text = str(payload.get("text", "AUTONOM"))
        repeat = max(1, min(int(payload.get("repeat", 1)), 10))

        await context.report_progress(25.0, "Validating input parameters", stage="validation")
        await asyncio.sleep(0.05)

        await context.report_progress(50.0, "Transforming text payload", stage="processing")
        reversed_text = text[::-1]
        repeated_text = " ".join([reversed_text] * repeat)
        await asyncio.sleep(0.05)

        await context.report_progress(100.0, "Echo transformation completed", stage="finalizing")
        return {
            "original_text": text,
            "transformed_text": repeated_text,
            "length": len(repeated_text),
            "repeat_count": repeat,
            "status": "success",
        }


class SleepProgressHandler(TaskHandler):
    """Cancellable, bounded demonstration handler that reports progressive status updates."""

    async def execute(self, payload: dict[str, Any], context: TaskExecutionContext) -> dict[str, Any]:
        steps = max(1, min(int(payload.get("steps", 5)), 20))
        step_delay = max(0.05, min(float(payload.get("step_delay", 0.3)), 5.0))
        fail_at_step = payload.get("fail_at_step")

        for step in range(1, steps + 1):
            # Cooperative cancellation check
            if context.is_cancellation_requested():
                raise TaskCancelledError(
                    task_id=context.task_id,
                    reason=f"Cancellation requested at step {step}/{steps}",
                )

            # Optional simulated failure
            if fail_at_step is not None and step == int(fail_at_step):
                raise TaskExecutionError(
                    message=f"Simulated execution failure at step {step} of {steps}.",
                    task_id=context.task_id,
                    retryable=False,
                )

            percent = round((step / steps) * 100.0, 1)
            msg = f"Executing step {step} of {steps} ({percent}%)"
            await context.report_progress(percent, msg, stage=f"step_{step}")
            await asyncio.sleep(step_delay)

        return {
            "steps_completed": steps,
            "step_delay": step_delay,
            "message": f"Successfully completed all {steps} progress steps.",
            "status": "success",
        }


class AIGenerateHandler(TaskHandler):
    """Executes unified AI text generation via the AI Gateway."""

    async def execute(self, payload: dict[str, Any], context: TaskExecutionContext) -> dict[str, Any]:
        from app.ai.contracts import ChatMessage, InferenceRequest, RoutingStrategy, TaskCategory
        from app.ai.factory import get_ai_gateway

        gateway = get_ai_gateway()
        await context.report_progress(10.0, "Validating inference request parameters", stage="validation")

        prompt = payload.get("prompt", "")
        system_prompt = payload.get("system_prompt")
        category_str = payload.get("category", TaskCategory.GENERAL_CONVERSATION.value)
        strategy_str = payload.get("strategy", RoutingStrategy.LOCAL_FIRST.value)

        messages = [ChatMessage(role="user", content=prompt)]
        req = InferenceRequest(
            task_id=context.task_id,
            task_category=TaskCategory(category_str)
            if category_str in TaskCategory._value2member_map_
            else TaskCategory.GENERAL_CONVERSATION,
            routing_strategy=RoutingStrategy(strategy_str)
            if strategy_str in RoutingStrategy._value2member_map_
            else RoutingStrategy.LOCAL_FIRST,
            messages=messages,
            system_prompt=system_prompt,
            provider_preference=payload.get("provider"),
            model_preference=payload.get("model"),
            temperature=float(payload.get("temperature", 0.7)),
            max_tokens=int(payload.get("max_tokens", 4096)),
            is_local_only=bool(payload.get("is_local_only", False)),
        )

        await context.report_progress(30.0, "Dispatching inference through AI Model Gateway", stage="dispatch")

        if context.is_cancellation_requested():
            raise TaskCancelledError(task_id=context.task_id, reason="Cancelled prior to generation")

        res = await gateway.generate(req)

        await context.report_progress(100.0, "Inference completed successfully", stage="finalizing")
        return {
            "request_id": res.request_id,
            "provider_id": res.provider_id,
            "model_id": res.model_id,
            "content": res.content,
            "usage": res.usage.model_dump(),
            "latency_ms": res.latency_ms,
            "estimated_cost_usd": res.estimated_cost_usd,
            "status": "success",
        }


class AIGenerateStructuredHandler(TaskHandler):
    """Executes structured JSON inference conforming to target schema."""

    async def execute(self, payload: dict[str, Any], context: TaskExecutionContext) -> dict[str, Any]:
        from app.ai.contracts import ChatMessage, InferenceRequest, RoutingStrategy, TaskCategory
        from app.ai.factory import get_ai_gateway

        gateway = get_ai_gateway()
        await context.report_progress(15.0, "Validating structured schema and input prompt", stage="validation")

        prompt = payload.get("prompt", "")
        schema = payload.get("schema")
        category_str = payload.get("category", TaskCategory.STRUCTURED_EXTRACTION.value)

        req = InferenceRequest(
            task_id=context.task_id,
            task_category=TaskCategory(category_str)
            if category_str in TaskCategory._value2member_map_
            else TaskCategory.STRUCTURED_EXTRACTION,
            routing_strategy=RoutingStrategy.LOCAL_FIRST,
            messages=[ChatMessage(role="user", content=prompt)],
            system_prompt=payload.get("system_prompt"),
            provider_preference=payload.get("provider"),
            model_preference=payload.get("model"),
            response_format="json_schema" if schema else "json_object",
            json_schema=schema,
        )

        await context.report_progress(40.0, "Executing structured output generation", stage="inference")
        res = await gateway.generate_structured(req, target_schema=schema)

        await context.report_progress(100.0, "Structured validation completed", stage="finalizing")
        return {
            "request_id": res.request_id,
            "provider_id": res.provider_id,
            "model_id": res.model_id,
            "structured_data": res.structured_data,
            "content": res.content,
            "usage": res.usage.model_dump(),
            "latency_ms": res.latency_ms,
            "status": "success",
        }


class AIClassifyHandler(TaskHandler):
    """Classifies input text into one of several predefined label categories."""

    async def execute(self, payload: dict[str, Any], context: TaskExecutionContext) -> dict[str, Any]:
        from app.ai.contracts import ChatMessage, InferenceRequest, TaskCategory
        from app.ai.factory import get_ai_gateway

        gateway = get_ai_gateway()
        text = payload.get("text", "")
        categories = payload.get("categories", ["positive", "neutral", "negative"])

        await context.report_progress(
            20.0, f"Classifying text across {len(categories)} categories", stage="classifying"
        )

        prompt = f'Classify the following text into exactly one of these categories: {json.dumps(categories)}.\n\nText:\n{text}\n\nRespond with a JSON object: {{"category": "chosen_category", "confidence": 0.0-1.0, "rationale": "brief reason"}}'
        schema = {
            "type": "object",
            "properties": {
                "category": {"type": "string", "enum": categories},
                "confidence": {"type": "number"},
                "rationale": {"type": "string"},
            },
            "required": ["category", "confidence"],
        }

        req = InferenceRequest(
            task_id=context.task_id,
            task_category=TaskCategory.CLASSIFICATION,
            messages=[ChatMessage(role="user", content=prompt)],
            response_format="json_schema",
            json_schema=schema,
        )

        res = await gateway.generate_structured(req, target_schema=schema)
        await context.report_progress(100.0, "Classification complete", stage="finalizing")
        return {
            "result": res.structured_data,
            "provider_id": res.provider_id,
            "model_id": res.model_id,
            "latency_ms": res.latency_ms,
            "status": "success",
        }


class AISummarizeHandler(TaskHandler):
    """Summarizes text within specified word count limits."""

    async def execute(self, payload: dict[str, Any], context: TaskExecutionContext) -> dict[str, Any]:
        from app.ai.contracts import ChatMessage, InferenceRequest, TaskCategory
        from app.ai.factory import get_ai_gateway

        gateway = get_ai_gateway()
        text = payload.get("text", "")
        max_words = int(payload.get("max_words", 100))

        await context.report_progress(20.0, f"Generating summary (target max {max_words} words)", stage="summarizing")

        prompt = f"Please summarize the following text in no more than {max_words} words concisely while preserving critical facts:\n\n{text}"
        req = InferenceRequest(
            task_id=context.task_id,
            task_category=TaskCategory.SUMMARIZATION,
            messages=[ChatMessage(role="user", content=prompt)],
            temperature=0.3,
            max_tokens=max_words * 3,
        )

        res = await gateway.generate(req)
        await context.report_progress(100.0, "Summary complete", stage="finalizing")
        return {
            "summary": res.content,
            "provider_id": res.provider_id,
            "model_id": res.model_id,
            "latency_ms": res.latency_ms,
            "usage": res.usage.model_dump(),
            "status": "success",
        }


class HandlerRegistry:
    """Registry maintaining approved executable task handlers."""

    def __init__(self) -> None:
        self._handlers: dict[str, TaskHandler] = {}
        # Register safe built-in demonstration handlers
        self.register("compute.echo", ComputeEchoHandler())
        self.register("test.sleep_progress", SleepProgressHandler())
        # Register AI inference handlers
        self.register("ai.generate", AIGenerateHandler())
        self.register("ai.generate_structured", AIGenerateStructuredHandler())
        self.register("ai.classify", AIClassifyHandler())
        self.register("ai.summarize", AISummarizeHandler())

    def register(self, task_type: str, handler: TaskHandler) -> None:
        """Registers a task handler under a distinct task type key."""
        self._handlers[task_type] = handler

    def get(self, task_type: str) -> TaskHandler:
        """Retrieves handler for task type or raises UnknownTaskTypeError."""
        handler = self._handlers.get(task_type)
        if not handler:
            raise UnknownTaskTypeError(task_type, list(self._handlers.keys()))
        return handler

    def list_types(self) -> list[str]:
        """Returns list of all currently registered task type identifiers."""
        return sorted(self._handlers.keys())
