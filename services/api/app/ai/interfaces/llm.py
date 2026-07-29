"""
app/ai/interfaces/llm.py

Vendor-neutral abstraction for large language model providers
(Azure OpenAI, OpenAI, Anthropic, Gemini, Ollama, LM Studio, OpenRouter, ...).
"""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, AsyncIterator

from app.ai.interfaces.base import BaseProvider


@dataclass
class LLMMessage:
    role: str  # "system" | "user" | "assistant" | "tool"
    content: str
    name: str | None = None


@dataclass
class LLMRequest:
    messages: list[LLMMessage]
    model: str | None = None
    temperature: float = 0.7
    max_tokens: int | None = None
    stop: list[str] | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class TokenUsage:
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total_tokens(self) -> int:
        return self.prompt_tokens + self.completion_tokens


@dataclass
class LLMResponse:
    content: str
    model: str
    usage: TokenUsage = field(default_factory=TokenUsage)
    finish_reason: str = "stop"
    raw: dict[str, Any] = field(default_factory=dict)


@dataclass
class LLMChunk:
    delta: str
    finished: bool = False


class LLMProvider(BaseProvider):
    """Contract for chat/completion large language model providers."""

    @abstractmethod
    async def generate(self, request: LLMRequest) -> LLMResponse:
        """Produce a single completion for the given request."""
        raise NotImplementedError

    async def stream(self, request: LLMRequest) -> AsyncIterator[LLMChunk]:
        """Stream a completion. Default falls back to a single chunk.

        Providers that support real streaming should override this and
        advertise the "streaming" capability.
        """
        response = await self.generate(request)
        yield LLMChunk(delta=response.content, finished=True)
