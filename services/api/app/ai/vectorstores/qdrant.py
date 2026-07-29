from __future__ import annotations

from typing import Any

from qdrant_client import AsyncQdrantClient
from qdrant_client.http.models import Distance, FieldCondition, Filter, MatchAny, MatchValue, PointStruct, VectorParams

from app.ai.exceptions.errors import VectorStoreError
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.vectorstore import VectorMatch, VectorQuery, VectorRecord, VectorStoreProvider


class QdrantVectorStoreProvider(VectorStoreProvider):
    provider_name = "qdrant"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        super().__init__(config)
        self._client: AsyncQdrantClient | None = None
        self._url = self._config.get("url")
        self._api_key = self._config.get("api_key")
        self._distance = self._config.get("distance", "cosine").lower()

    async def initialize(self) -> None:
        self._client = AsyncQdrantClient(url=self._url, api_key=self._api_key)
        await super().initialize()

    def _distance_enum(self) -> Distance:
        mapping = {"cosine": Distance.COSINE, "dot": Distance.DOT, "euclid": Distance.EUCLID}
        return mapping.get(self._distance, Distance.COSINE)

    async def _ensure_collection(self, collection: str, dimensions: int) -> None:
        assert self._client is not None
        collections = await self._client.get_collections()
        names = {item.name for item in collections.collections}
        if collection in names:
            return
        await self._client.create_collection(
            collection_name=collection,
            vectors_config=VectorParams(size=dimensions, distance=self._distance_enum()),
        )

    def _to_filter(self, filters: dict[str, Any]) -> Filter | None:
        if not filters:
            return None
        conditions: list[FieldCondition] = []
        for key, value in filters.items():
            if isinstance(value, (list, tuple)):
                conditions.append(FieldCondition(key=key, match=MatchAny(any=list(value))))
            else:
                conditions.append(FieldCondition(key=key, match=MatchValue(value=value)))
        return Filter(must=conditions)

    async def upsert(self, collection: str, records: list[VectorRecord]) -> None:
        if self._client is None:
            raise VectorStoreError("Qdrant client not initialized.", provider=self.provider_name, category="vectorstore")
        if not records:
            return

        dimensions = len(records[0].vector)
        await self._ensure_collection(collection, dimensions)

        points = [PointStruct(id=record.id, vector=record.vector, payload=record.metadata) for record in records]
        await self._client.upsert(collection_name=collection, points=points)

    async def query(self, collection: str, query: VectorQuery) -> list[VectorMatch]:
        if self._client is None:
            raise VectorStoreError("Qdrant client not initialized.", provider=self.provider_name, category="vectorstore")

        result = await self._client.search(
            collection_name=collection,
            query_vector=query.vector,
            query_filter=self._to_filter(query.filters),
            limit=query.top_k,
            with_payload=True,
        )
        return [
            VectorMatch(
                id=str(item.id),
                score=float(item.score),
                metadata=dict(item.payload or {}),
            )
            for item in result
        ]

    async def delete(self, collection: str, ids: list[str]) -> None:
        if self._client is None:
            raise VectorStoreError("Qdrant client not initialized.", provider=self.provider_name, category="vectorstore")
        if not ids:
            return
        await self._client.delete(collection_name=collection, points_selector=ids)

    async def health(self) -> HealthCheckResult:
        if not self._url:
            return HealthCheckResult(status=HealthStatus.UNHEALTHY, message="QDRANT_URL not configured.")
        return HealthCheckResult(status=HealthStatus.HEALTHY, message="Qdrant vector store configured.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"collections", "metadata-filter", "pagination"}))

    def validate(self) -> list[str]:
        return [] if self._url else ["Missing Qdrant URL."]
