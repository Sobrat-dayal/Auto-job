"""Unified AI Model Gateway coordinating providers, routing, hardware limits, and streaming."""

import json
import logging
from typing import Any, AsyncIterator

from app.ai.budgets import budget_manager
from app.ai.cancellation import cancellation_manager
from app.ai.context import context_manager
from app.ai.contracts import (
    HardwareTelemetry,
    InferenceChunk,
    InferenceRequest,
    InferenceResponse,
    RoutingDecision,
)
from app.ai.errors import (
    AIGatewayError,
    InvalidStructuredOutputError,
    ProviderUnavailableError,
)
from app.ai.registry import ProviderRegistry
from app.ai.resources.controller import resource_controller
from app.ai.router import IntelligentModelRouter
from app.ai.streaming import StreamingCoordinator

logger = logging.getLogger("autonom.ai.gateway")


class AIGateway:
    """Unified inference orchestration facade for AUTONOM desktop and autonomous agents."""

    def __init__(self, registry: ProviderRegistry | None = None) -> None:
        self.registry = registry or ProviderRegistry()
        self.router = IntelligentModelRouter(self.registry)
        self.resource_controller = resource_controller
        self.context_manager = context_manager
        self.budget_manager = budget_manager
        self.cancellation_manager = cancellation_manager
        self._on_request_completed_callbacks: list[Any] = []

    def register_completion_callback(self, callback: Any) -> None:
        """Registers a callback hook invoked when an inference request completes."""
        self._on_request_completed_callbacks.append(callback)

    async def preview_route(self, request: InferenceRequest) -> RoutingDecision:
        """Returns explainable routing preview without executing actual inference."""
        if not self.registry.list_models():
            await self.registry.discover_all_models()
        return self.router.select_model(request)

    async def generate(self, request: InferenceRequest) -> InferenceResponse:
        """Executes complete non-streaming inference with routing, resource controls, and fallback."""
        if not self.registry.list_models():
            await self.registry.discover_all_models()

        # 1. Routing decision
        decision = self.router.select_model(request)
        provider = self.registry.get(decision.selected_provider_id)
        model_info = self.registry.get_model(decision.selected_provider_id, decision.selected_model_id)

        # 2. Context budgeting & validation
        context_limit = model_info.context_window if model_info else 8192
        validated_messages, est_usage, _ = self.context_manager.prepare_and_validate_context(
            messages=request.messages,
            system_prompt=request.system_prompt,
            context_window=context_limit,
            max_output_tokens=request.max_tokens,
            model_id=decision.selected_model_id,
            auto_truncate=True,
        )
        request = request.model_copy(update={"messages": validated_messages})

        # 3. Budget estimation and check
        est_cost = self.budget_manager.calculate_cost(
            provider.provider_id,
            decision.selected_model_id,
            est_usage.prompt_tokens,
            request.max_tokens,
        )
        self.budget_manager.validate_budget(est_cost, request.max_cost_usd)

        # 4. Register cancellation token
        self.cancellation_manager.register(request.request_id)

        try:
            # 5. Local resource scheduling if target is local
            if provider.provider_type == "local":
                async with self.resource_controller.acquire_local_slot():
                    await self.resource_controller.ensure_model_ready(
                        target_model_id=decision.selected_model_id,
                        provider_unload_fn=provider.unload_model,
                        provider_load_fn=provider.load_model,
                    )
                    response = await provider.generate(
                        request.model_copy(update={"model_preference": decision.selected_model_id})
                    )
            else:
                response = await provider.generate(
                    request.model_copy(update={"model_preference": decision.selected_model_id})
                )

            # Attach routing metadata
            response.routing_decision = decision

            # Trigger persistence callbacks
            for cb in self._on_request_completed_callbacks:
                try:
                    await cb(request, response)
                except Exception as exc:
                    logger.warning(f"Error in request completion callback: {exc}")

            return response

        except Exception as exc:
            logger.warning(
                f"Primary model execution failed ({decision.selected_provider_id}:{decision.selected_model_id}): {exc}"
            )

            # 6. Attempt fallback if permitted
            fallback_decision = self.router.resolve_fallback(
                request=request,
                failed_provider_id=decision.selected_provider_id,
                failed_model_id=decision.selected_model_id,
            )
            if fallback_decision:
                logger.info(
                    f"Executing fallback to {fallback_decision.selected_provider_id}:{fallback_decision.selected_model_id}"
                )
                fallback_provider = self.registry.get(fallback_decision.selected_provider_id)
                fallback_req = request.model_copy(update={"model_preference": fallback_decision.selected_model_id})

                if fallback_provider.provider_type == "local":
                    async with self.resource_controller.acquire_local_slot():
                        await self.resource_controller.ensure_model_ready(
                            target_model_id=fallback_decision.selected_model_id,
                            provider_unload_fn=fallback_provider.unload_model,
                            provider_load_fn=fallback_provider.load_model,
                        )
                        fallback_res = await fallback_provider.generate(fallback_req)
                else:
                    fallback_res = await fallback_provider.generate(fallback_req)

                fallback_res.routing_decision = fallback_decision
                for cb in self._on_request_completed_callbacks:
                    try:
                        await cb(request, fallback_res)
                    except Exception:
                        pass
                return fallback_res

            # Re-raise normalized error if no fallback succeeded
            if isinstance(exc, AIGatewayError):
                raise
            raise ProviderUnavailableError(decision.selected_provider_id, str(exc)) from exc

        finally:
            self.cancellation_manager.unregister(request.request_id)

    async def generate_structured(
        self,
        request: InferenceRequest,
        target_schema: dict[str, Any] | None = None,
    ) -> InferenceResponse:
        """Executes inference requesting structured JSON output with automatic validation and repair retry."""
        req = request.model_copy(
            update={
                "response_format": "json_schema" if target_schema else "json_object",
                "json_schema": target_schema,
                "required_capabilities": list(set(request.required_capabilities + ["structured_output"])),
            }
        )

        response = await self.generate(req)

        # Validate that JSON parsed properly
        if response.structured_data is None:
            try:
                response.structured_data = json.loads(response.content)
            except Exception as exc:
                logger.warning(
                    f"Initial structured output parsing failed: {exc}. Retrying with strict JSON instruction..."
                )
                # One automatic retry with explicit system repair directive
                repair_req = req.model_copy(
                    update={
                        "system_prompt": (req.system_prompt or "") + "\nCRITICAL: Respond with pure valid JSON only.",
                    }
                )
                retry_res = await self.generate(repair_req)
                try:
                    retry_res.structured_data = json.loads(retry_res.content)
                    return retry_res
                except Exception as retry_exc:
                    raise InvalidStructuredOutputError(retry_res.content, str(retry_exc)) from retry_exc

        return response

    async def stream(self, request: InferenceRequest) -> AsyncIterator[str]:
        """Provides SSE token stream with routing metadata and cancellation handling."""
        decision = self.router.select_model(request)
        provider = self.registry.get(decision.selected_provider_id)
        model_info = self.registry.get_model(decision.selected_provider_id, decision.selected_model_id)

        context_limit = model_info.context_window if model_info else 8192
        validated_messages, _, _ = self.context_manager.prepare_and_validate_context(
            messages=request.messages,
            system_prompt=request.system_prompt,
            context_window=context_limit,
            max_output_tokens=request.max_tokens,
            model_id=decision.selected_model_id,
            auto_truncate=True,
        )
        request = request.model_copy(
            update={
                "messages": validated_messages,
                "model_preference": decision.selected_model_id,
            }
        )

        self.cancellation_manager.register(request.request_id)

        async def _stream_producer() -> AsyncIterator[InferenceChunk]:
            try:
                if provider.provider_type == "local":
                    async with self.resource_controller.acquire_local_slot():
                        await self.resource_controller.ensure_model_ready(
                            target_model_id=decision.selected_model_id,
                            provider_unload_fn=provider.unload_model,
                            provider_load_fn=provider.load_model,
                        )
                        async for chunk in provider.stream(request):
                            yield chunk
                else:
                    async for chunk in provider.stream(request):
                        yield chunk
            finally:
                self.cancellation_manager.unregister(request.request_id)

        async for sse_msg in StreamingCoordinator.wrap_stream(
            request_id=request.request_id,
            routing_decision=decision,
            chunk_iterator=_stream_producer(),
        ):
            yield sse_msg

    def cancel(self, request_id: str) -> bool:
        """Cooperatively cancels an ongoing generation."""
        return self.cancellation_manager.cancel(request_id)

    def get_hardware_telemetry(self) -> HardwareTelemetry:
        """Returns real host hardware telemetry."""
        return self.resource_controller.get_telemetry()
