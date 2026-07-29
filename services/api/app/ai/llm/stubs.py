"""
app/ai/llm/stubs.py

Lightweight stub providers for future LLM vendors. Each stub satisfies the
`LLMProvider` contract (so it can be registered and resolved today) but
performs no network calls and raises `LLMError` if invoked, until a real
implementation is added behind the same interface.
"""
from __future__ import annotations

from app.ai.exceptions.errors import LLMError
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.llm import LLMProvider, LLMRequest, LLMResponse


class _StubLLMProvider(LLMProvider):
    """Base for not-yet-implemented LLM vendor integrations."""

    async def generate(self, request: LLMRequest) -> LLMResponse:
        raise LLMError(
            f"'{self.provider_name}' is a stub provider. Implement generate() to enable it.",
            provider=self.provider_name,
            category="llm",
        )

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(
            status=HealthStatus.UNKNOWN,
            message=f"'{self.provider_name}' is a stub — not implemented.",
        )

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset(), metadata={"stub": True})

    def validate(self) -> list[str]:
        return [f"'{self.provider_name}' is a stub provider and cannot be used in production."]


class AzureOpenAIProvider(_StubLLMProvider):
    provider_name = "azure-openai"


class OpenAIProvider(_StubLLMProvider):
    provider_name = "openai"


class AnthropicProvider(_StubLLMProvider):
    provider_name = "anthropic"


class GeminiProvider(_StubLLMProvider):
    provider_name = "gemini"


class OllamaProvider(_StubLLMProvider):
    provider_name = "ollama"


class LMStudioProvider(_StubLLMProvider):
    provider_name = "lm-studio"


class OpenRouterProvider(_StubLLMProvider):
    provider_name = "openrouter"
