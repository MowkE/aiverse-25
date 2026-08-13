"""Provider adapters: deterministic mock plus guarded real HTTP providers."""

from .base import LLMRequest, LLMResponse, MissingAPIKeyError, Provider
from .mock import MockProvider

__all__ = [
    "LLMRequest",
    "LLMResponse",
    "MissingAPIKeyError",
    "MockProvider",
    "Provider",
    "make_provider",
]


def make_provider(name: str, model: str, guard=None):
    """Factory used by the CLI. Real providers require an armed BudgetGuard."""
    if name == "mock":
        return MockProvider()
    if name == "anthropic":
        from .anthropic_provider import AnthropicProvider

        return AnthropicProvider(guard=guard)
    if name == "openai":
        from .openai_provider import OpenAIProvider

        return OpenAIProvider(guard=guard)
    if name == "claude-cli":
        from .claude_cli import ClaudeCLIProvider

        return ClaudeCLIProvider(guard=guard)
    raise ValueError(f"unknown provider {name!r}")
