"""
app/ai/retrieval/ragflow.py

Stub for a future RAGFlow-backed retrieval provider. Satisfies the
`RetrievalProvider` contract; raises `RetrievalError` if invoked until a
real implementation (behind this same interface) replaces it.
"""
from __future__ import annotations

from app.ai.exceptions.errors import RetrievalError
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.retrieval import RetrievalProvider, RetrievalQuery, RetrievalResult


class RAGFlowProvider(RetrievalProvider):
    provider_name = "ragflow"

    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        raise RetrievalError(
            "'ragflow' is a stub provider. Implement retrieve() to enable it.",
            provider=self.provider_name,
            category="retrieval",
        )

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.UNKNOWN, message="'ragflow' is a stub — not implemented.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset(), metadata={"stub": True})

    def validate(self) -> list[str]:
        return ["'ragflow' is a stub provider and cannot be used in production."]
