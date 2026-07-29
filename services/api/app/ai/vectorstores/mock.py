"""
app/ai/vectorstores/mock.py

In-memory vector store for local development and tests. Uses naive
cosine similarity — fine for exercising the pipeline, not for production.
"""
from __future__ import annotations

import math

from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.vectorstore import VectorMatch, VectorQuery, VectorRecord, VectorStoreProvider


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(y * y for y in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class MockVectorStoreProvider(VectorStoreProvider):
    provider_name = "mock"

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)
        self._collections: dict[str, dict[str, VectorRecord]] = {}

    async def upsert(self, collection: str, records: list[VectorRecord]) -> None:
        store = self._collections.setdefault(collection, {})
        for record in records:
            store[record.id] = record

    async def query(self, collection: str, query: VectorQuery) -> list[VectorMatch]:
        store = self._collections.get(collection, {})
        scored = [
            VectorMatch(id=r.id, score=_cosine_similarity(query.vector, r.vector), metadata=r.metadata)
            for r in store.values()
        ]
        scored.sort(key=lambda m: m.score, reverse=True)
        return scored[: query.top_k]

    async def delete(self, collection: str, ids: list[str]) -> None:
        store = self._collections.get(collection, {})
        for record_id in ids:
            store.pop(record_id, None)

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.HEALTHY, message="Mock vector store provider is always healthy.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"upsert", "cosine-similarity"}))
