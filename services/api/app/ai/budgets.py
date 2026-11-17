"""Token pricing, cost estimation, and spending budget enforcement."""

from app.ai.contracts import ModelPricing
from app.ai.errors import BudgetExceededError

# Standard verified cloud pricing rates per 1M tokens (USD)
PRICING_CATALOG: dict[str, ModelPricing] = {
    # Local models: always 0.00
    "ollama:default": ModelPricing(input_cost_per_million=0.0, output_cost_per_million=0.0),
    # OpenAI models
    "openai:gpt-4o": ModelPricing(input_cost_per_million=2.50, output_cost_per_million=10.00),
    "openai:gpt-4o-mini": ModelPricing(input_cost_per_million=0.15, output_cost_per_million=0.60),
    "openai:o1-preview": ModelPricing(input_cost_per_million=15.00, output_cost_per_million=60.00),
    "openai:o1-mini": ModelPricing(input_cost_per_million=3.00, output_cost_per_million=12.00),
    # Anthropic models (reference)
    "anthropic:claude-3-5-sonnet-20241022": ModelPricing(input_cost_per_million=3.00, output_cost_per_million=15.00),
    "anthropic:claude-3-5-haiku-20241022": ModelPricing(input_cost_per_million=0.80, output_cost_per_million=4.00),
    # DeepSeek models
    "deepseek:deepseek-chat": ModelPricing(input_cost_per_million=0.14, output_cost_per_million=0.28),
    "deepseek:deepseek-coder": ModelPricing(input_cost_per_million=0.14, output_cost_per_million=0.28),
}


class TokenBudgetManager:
    """Manages token accounting and computes estimated inference costs."""

    def __init__(self) -> None:
        self._pricing = dict(PRICING_CATALOG)

    def get_pricing(self, provider_id: str, model_id: str) -> ModelPricing:
        """Looks up pricing rate for model or provider."""
        key = f"{provider_id}:{model_id}"
        if key in self._pricing:
            return self._pricing[key]
        if provider_id == "ollama":
            return self._pricing["ollama:default"]
        # Generic default for unknown cloud models: $1.00 / $2.00 estimate
        return ModelPricing(input_cost_per_million=1.00, output_cost_per_million=2.00)

    def calculate_cost(
        self,
        provider_id: str,
        model_id: str,
        prompt_tokens: int,
        completion_tokens: int,
    ) -> float:
        """Calculates cost in USD for given token usage."""
        pricing = self.get_pricing(provider_id, model_id)
        input_cost = (prompt_tokens / 1_000_000.0) * pricing.input_cost_per_million
        output_cost = (completion_tokens / 1_000_000.0) * pricing.output_cost_per_million
        return round(input_cost + output_cost, 6)

    def validate_budget(self, estimated_cost: float, max_budget_usd: float | None) -> None:
        """Validates estimated cost against request budget cap."""
        if max_budget_usd is not None and estimated_cost > max_budget_usd:
            raise BudgetExceededError(estimated_cost=estimated_cost, max_budget=max_budget_usd)


budget_manager = TokenBudgetManager()
