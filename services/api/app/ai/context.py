"""Context window budget management, token counting, and message truncation."""

import logging

from app.ai.contracts import ChatMessage, TokenUsage
from app.ai.errors import ContextLimitExceededError

logger = logging.getLogger("autonom.ai.context")


class ContextBudgetManager:
    """Calculates token counts, reserves output budgets, and safely truncates messages."""

    def __init__(self) -> None:
        self._tiktoken_enc = None
        try:
            import tiktoken

            self._tiktoken_enc = tiktoken.get_encoding("cl100k_base")
        except Exception:
            logger.debug("tiktoken not available, using heuristic token estimation.")

    def count_tokens(self, text: str, model_id: str = "") -> int:
        """Counts or estimates token length of given string."""
        if not text:
            return 0
        if self._tiktoken_enc is not None:
            try:
                return len(self._tiktoken_enc.encode(text))
            except Exception:
                pass
        # Robust heuristic fallback: 1 token ≈ 4 characters
        return max(1, len(text) // 4)

    def count_messages_tokens(self, messages: list[ChatMessage], system_prompt: str | None = None) -> int:
        """Counts total tokens for a sequence of chat messages including envelope overhead."""
        total = 0
        if system_prompt:
            total += self.count_tokens(system_prompt) + 4  # System prompt message overhead

        for msg in messages:
            # 4 tokens per message overhead in chat completion format (<|im_start|>role\ncontent<|im_end|>)
            total += 4
            total += self.count_tokens(msg.content)
            if msg.name:
                total += self.count_tokens(msg.name)

        total += 2  # priming tokens for assistant reply
        return total

    def prepare_and_validate_context(
        self,
        messages: list[ChatMessage],
        system_prompt: str | None,
        context_window: int,
        max_output_tokens: int,
        model_id: str,
        auto_truncate: bool = True,
    ) -> tuple[list[ChatMessage], TokenUsage, bool]:
        """Validates that messages fit within context budget; truncates old history if auto_truncate is True."""
        required_output_reserve = max(256, max_output_tokens)
        available_input_budget = max(256, context_window - required_output_reserve)

        current_input_tokens = self.count_messages_tokens(messages, system_prompt)

        if current_input_tokens <= available_input_budget:
            usage = TokenUsage(prompt_tokens=current_input_tokens, source="estimated")
            return messages, usage, False

        if not auto_truncate:
            raise ContextLimitExceededError(
                prompt_tokens=current_input_tokens + required_output_reserve,
                context_limit=context_window,
                model_id=model_id,
            )

        # Auto-truncation strategy:
        # Keep the latest user message and prune oldest intermediate messages
        truncated = list(messages)
        was_truncated = False

        while len(truncated) > 1 and self.count_messages_tokens(truncated, system_prompt) > available_input_budget:
            # Drop the oldest message that isn't the final one
            truncated.pop(0)
            was_truncated = True

        final_tokens = self.count_messages_tokens(truncated, system_prompt)
        usage = TokenUsage(prompt_tokens=final_tokens, source="estimated")
        return truncated, usage, was_truncated


context_manager = ContextBudgetManager()
