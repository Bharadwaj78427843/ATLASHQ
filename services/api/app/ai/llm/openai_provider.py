from __future__ import annotations

import asyncio
from typing import Any, AsyncIterator

from openai import AsyncOpenAI
from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError

from app.ai.exceptions.errors import LLMError
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.llm import LLMChunk, LLMProvider, LLMRequest, LLMResponse, TokenUsage


class OpenAILLMProvider(LLMProvider):
    provider_name = "openai"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._client: AsyncOpenAI | None = None
        self._api_key = self._config.get("api_key")
        self._model = self._config.get("model", "gpt-4o-mini")
        self._timeout = float(self._config.get("timeout_seconds", 30))
        self._max_retries = int(self._config.get("max_retries", 3))

    async def initialize(self) -> None:
        self._client = AsyncOpenAI(api_key=self._api_key, timeout=self._timeout)
        await super().initialize()

    def _messages(self, request: LLMRequest) -> list[dict[str, str]]:
        return [{"role": m.role, "content": m.content} for m in request.messages]

    async def _with_retries(self, coro_factory):
        attempt = 0
        while True:
            try:
                return await coro_factory()
            except (RateLimitError, APITimeoutError, APIConnectionError, APIError) as exc:
                attempt += 1
                if attempt > self._max_retries:
                    raise LLMError(
                        f"OpenAI request failed after {self._max_retries} retries: {exc}",
                        provider=self.provider_name,
                        category="llm",
                    ) from exc
                await asyncio.sleep(min(2**attempt, 8))

    async def generate(self, request: LLMRequest) -> LLMResponse:
        if self._client is None:
            raise LLMError("OpenAI client is not initialized.", provider=self.provider_name, category="llm")

        async def call():
            return await self._client.chat.completions.create(
                model=request.model or self._model,
                messages=self._messages(request),
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stop=request.stop,
                stream=False,
            )

        response = await self._with_retries(call)
        choice = response.choices[0]
        usage = response.usage
        return LLMResponse(
            content=choice.message.content or "",
            model=response.model,
            usage=TokenUsage(
                prompt_tokens=int(getattr(usage, "prompt_tokens", 0) or 0),
                completion_tokens=int(getattr(usage, "completion_tokens", 0) or 0),
            ),
            finish_reason=choice.finish_reason or "stop",
            raw=response.model_dump(),
        )

    async def stream(self, request: LLMRequest) -> AsyncIterator[LLMChunk]:
        if self._client is None:
            raise LLMError("OpenAI client is not initialized.", provider=self.provider_name, category="llm")
        stream = await self._client.chat.completions.create(
            model=request.model or self._model,
            messages=self._messages(request),
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stop=request.stop,
            stream=True,
        )
        async for chunk in stream:
            delta = chunk.choices[0].delta.content or ""
            finished = chunk.choices[0].finish_reason is not None
            if delta or finished:
                yield LLMChunk(delta=delta, finished=finished)

    async def health(self) -> HealthCheckResult:
        if not self._api_key:
            return HealthCheckResult(status=HealthStatus.UNHEALTHY, message="OPENAI_API_KEY not configured.")
        return HealthCheckResult(status=HealthStatus.HEALTHY, message="OpenAI LLM provider configured.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"chat", "streaming", "retries"}))

    def validate(self) -> list[str]:
        problems: list[str] = []
        if not self._api_key:
            problems.append("Missing OpenAI API key.")
        return problems
