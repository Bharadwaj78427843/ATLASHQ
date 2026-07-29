"""
app/ai/embeddings/stubs.py

Lightweight stubs for future embedding vendors. Each satisfies the
`EmbeddingProvider` contract but raises `EmbeddingError` if invoked.
"""
from __future__ import annotations

from app.ai.exceptions.errors import EmbeddingError
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.embedding import EmbeddingProvider, EmbeddingRequest, EmbeddingResponse


class _StubEmbeddingProvider(EmbeddingProvider):
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        raise EmbeddingError(
            f"'{self.provider_name}' is a stub provider. Implement embed() to enable it.",
            provider=self.provider_name,
            category="embeddings",
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


class OpenAIEmbeddingProvider(_StubEmbeddingProvider):
    provider_name = "openai"


class AzureEmbeddingProvider(_StubEmbeddingProvider):
    provider_name = "azure"


class SentenceTransformersProvider(_StubEmbeddingProvider):
    provider_name = "sentence-transformers"


class VoyageAIProvider(_StubEmbeddingProvider):
    provider_name = "voyageai"


class OllamaEmbeddingProvider(_StubEmbeddingProvider):
    provider_name = "ollama"
