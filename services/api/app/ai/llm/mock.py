"""
app/ai/llm/mock.py

In-memory LLM provider used for local development and tests. Deterministic,
zero network calls, zero vendor SDKs.
"""
from __future__ import annotations

from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.llm import LLMProvider, LLMRequest, LLMResponse, TokenUsage


class MockLLMProvider(LLMProvider):
    """Echoes the last user message with a canned prefix. No external calls."""

    provider_name = "mock"

    async def generate(self, request: LLMRequest) -> LLMResponse:
        last_user = next((m.content for m in reversed(request.messages) if m.role == "user"), "")
        content = f"[mock-llm] {last_user}"
        return LLMResponse(
            content=content,
            model=request.model or "mock-llm-v1",
            usage=TokenUsage(prompt_tokens=len(last_user.split()), completion_tokens=len(content.split())),
            finish_reason="stop",
        )

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.HEALTHY, message="Mock LLM provider is always healthy.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"chat", "streaming"}))
