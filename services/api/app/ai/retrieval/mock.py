"""
app/ai/retrieval/mock.py

In-memory retrieval provider used for local development and tests.
"""
from __future__ import annotations

from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.retrieval import RetrievalProvider, RetrievalQuery, RetrievalResult, RetrievedChunk


class MockRetrievalProvider(RetrievalProvider):
    """Returns a fixed set of canned chunks regardless of the query."""

    provider_name = "mock"

    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        chunks = [
            RetrievedChunk(
                id=f"mock-chunk-{i}",
                content=f"Mock context chunk #{i} relevant to: {query.text!r}",
                score=round(1.0 - i * 0.1, 2),
                source_id="mock-source",
            )
            for i in range(1, min(query.top_k, 3) + 1)
        ]
        return RetrievalResult(chunks=chunks)

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.HEALTHY, message="Mock retrieval provider is always healthy.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"semantic-search"}))
