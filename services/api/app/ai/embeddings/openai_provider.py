from __future__ import annotations

import asyncio
from typing import Any

from openai import AsyncOpenAI
from openai import APIConnectionError, APIError, APITimeoutError, RateLimitError

from app.ai.exceptions.errors import EmbeddingError
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.embedding import EmbeddingProvider, EmbeddingRequest, EmbeddingResponse


class OpenAIEmbeddingProvider(EmbeddingProvider):
    provider_name = "openai"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._client: AsyncOpenAI | None = None
        self._api_key = self._config.get("api_key")
        self._model = self._config.get("model", "text-embedding-3-small")
        self._batch_size = int(self._config.get("batch_size", 64))
        self._timeout = float(self._config.get("timeout_seconds", 30))
        self._max_retries = int(self._config.get("max_retries", 3))

    async def initialize(self) -> None:
        self._client = AsyncOpenAI(api_key=self._api_key, timeout=self._timeout)
        await super().initialize()

    async def _with_retries(self, coro_factory):
        attempt = 0
        while True:
            try:
                return await coro_factory()
            except (RateLimitError, APITimeoutError, APIConnectionError, APIError) as exc:
                attempt += 1
                if attempt > self._max_retries:
                    raise EmbeddingError(
                        f"OpenAI embedding failed after {self._max_retries} retries: {exc}",
                        provider=self.provider_name,
                        category="embeddings",
                    ) from exc
                await asyncio.sleep(min(2**attempt, 8))

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        if self._client is None:
            raise EmbeddingError("OpenAI embedding client is not initialized.", provider=self.provider_name, category="embeddings")

        vectors: list[list[float]] = []
        for i in range(0, len(request.inputs), self._batch_size):
            batch = request.inputs[i : i + self._batch_size]

            async def call():
                return await self._client.embeddings.create(model=request.model or self._model, input=batch)

            response = await self._with_retries(call)
            vectors.extend([item.embedding for item in response.data])

        dimensions = len(vectors[0]) if vectors else 0
        return EmbeddingResponse(
            vectors=vectors,
            model=request.model or self._model,
            dimensions=dimensions,
            raw={"count": len(vectors), "batch_size": self._batch_size},
        )

    async def health(self) -> HealthCheckResult:
        if not self._api_key:
            return HealthCheckResult(status=HealthStatus.UNHEALTHY, message="OPENAI_API_KEY not configured.")
        return HealthCheckResult(status=HealthStatus.HEALTHY, message="OpenAI embedding provider configured.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"batch", "retries"}))

    def validate(self) -> list[str]:
        return [] if self._api_key else ["Missing OpenAI API key."]
