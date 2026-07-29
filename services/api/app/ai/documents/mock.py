"""
app/ai/documents/mock.py

In-memory document provider for local development and tests.
"""
from __future__ import annotations

from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.document import DocumentContent, DocumentProvider, DocumentQuery, DocumentRef


class MockDocumentProvider(DocumentProvider):
    provider_name = "mock"

    _FIXTURES: list[DocumentRef] = [
        DocumentRef(id="doc-1", name="welcome.md", uri="mock://welcome.md", mime_type="text/markdown"),
        DocumentRef(id="doc-2", name="architecture.md", uri="mock://architecture.md", mime_type="text/markdown"),
    ]

    async def list_documents(self, query: DocumentQuery) -> list[DocumentRef]:
        return list(self._FIXTURES)

    async def fetch(self, ref: DocumentRef) -> DocumentContent:
        text = f"# {ref.name}\n\nMock content for {ref.id}."
        return DocumentContent(ref=ref, content=text.encode("utf-8"), text=text)

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.HEALTHY, message="Mock document provider is always healthy.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"list", "fetch"}))
