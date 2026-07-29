"""
app/ai/embeddings/mock.py

Deterministic, hash-based embedding provider for local development and
tests. Not semantically meaningful — purely for exercising the pipeline
without a real model or network call.
"""
from __future__ import annotations

import hashlib

from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.embedding import EmbeddingProvider, EmbeddingRequest, EmbeddingResponse

_DIMENSIONS = 16


class MockEmbeddingProvider(EmbeddingProvider):
    provider_name = "mock"

    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        vectors = [self._hash_embed(text) for text in request.inputs]
        return EmbeddingResponse(vectors=vectors, model=request.model or "mock-embedding-v1", dimensions=_DIMENSIONS)

    @staticmethod
    def _hash_embed(text: str) -> list[float]:
        digest = hashlib.sha256(text.encode("utf-8")).digest()
        return [byte / 255.0 for byte in digest[:_DIMENSIONS]]

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.HEALTHY, message="Mock embedding provider is always healthy.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"batch"}), metadata={"dimensions": _DIMENSIONS})
