"""
app/ai/vectorstores/stubs.py

Lightweight stubs for future vector store vendors. Each satisfies the
`VectorStoreProvider` contract but raises `VectorStoreError` if invoked.
"""
from __future__ import annotations

from app.ai.exceptions.errors import VectorStoreError
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.vectorstore import VectorMatch, VectorQuery, VectorRecord, VectorStoreProvider


class _StubVectorStoreProvider(VectorStoreProvider):
    def _not_implemented(self) -> VectorStoreError:
        return VectorStoreError(
            f"'{self.provider_name}' is a stub provider. Implement its methods to enable it.",
            provider=self.provider_name,
            category="vectorstore",
        )

    async def upsert(self, collection: str, records: list[VectorRecord]) -> None:
        raise self._not_implemented()

    async def query(self, collection: str, query: VectorQuery) -> list[VectorMatch]:
        raise self._not_implemented()

    async def delete(self, collection: str, ids: list[str]) -> None:
        raise self._not_implemented()

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(
            status=HealthStatus.UNKNOWN,
            message=f"'{self.provider_name}' is a stub — not implemented.",
        )

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset(), metadata={"stub": True})

    def validate(self) -> list[str]:
        return [f"'{self.provider_name}' is a stub provider and cannot be used in production."]


class PgVectorProvider(_StubVectorStoreProvider):
    provider_name = "pgvector"


class QdrantProvider(_StubVectorStoreProvider):
    provider_name = "qdrant"


class WeaviateProvider(_StubVectorStoreProvider):
    provider_name = "weaviate"


class PineconeProvider(_StubVectorStoreProvider):
    provider_name = "pinecone"


class MilvusProvider(_StubVectorStoreProvider):
    provider_name = "milvus"


class RedisVectorProvider(_StubVectorStoreProvider):
    provider_name = "redis-vector"
