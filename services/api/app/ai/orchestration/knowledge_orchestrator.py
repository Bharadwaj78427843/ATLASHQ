"""
app/ai/orchestration/knowledge_orchestrator.py

Orchestrates the platform's canonical knowledge pipeline:

    Upload -> Extract -> Normalize -> Chunk -> Embed -> Index
    -> Retrieve -> Context Assembly -> LLM -> Response

Every stage resolves its provider through the `ProviderFactory` (which in
turn uses the `ProviderRegistry`); this module contains no vendor-specific
logic and no knowledge of which concrete provider is active for any
category. Swapping the embedding, vector store, retrieval, or LLM provider
is a configuration change, never a code change here.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from app.ai.factory.factory import ProviderFactory
from app.ai.knowledge.base import KnowledgeProvider
from app.ai.knowledge.models import (
    KnowledgeDeleteRequest,
    KnowledgeIngestRequest,
    KnowledgeSearchRequest,
    KnowledgeSearchResultChunk,
    KnowledgeStatus,
    KnowledgeSyncRequest,
)
from app.ai.interfaces.document import DocumentRef
from app.ai.telemetry.hooks import TelemetryContext, get_telemetry


@dataclass
class IngestResult:
    document_id: str
    chunks_indexed: int
    collection: str


@dataclass
class QueryResult:
    answer: str
    context_chunks: list[KnowledgeSearchResultChunk] = field(default_factory=list)
    model: str = ""


class KnowledgeOrchestrator:
    """Composes providers into the platform's upload -> ... -> response pipeline."""

    def __init__(
        self,
        factory: ProviderFactory,
        knowledge_provider: KnowledgeProvider,
        *,
        telemetry: TelemetryContext | None = None,
    ) -> None:
        self._factory = factory
        self._knowledge_provider = knowledge_provider
        self._telemetry = telemetry or get_telemetry()

    async def ingest(self, ref: DocumentRef, *, collection: str = "default") -> IngestResult:
        """Upload -> ... -> Index via the active KnowledgeProvider."""
        with self._telemetry.timed("ai.orchestration.ingest"):
            result = await self._knowledge_provider.ingest(
                KnowledgeIngestRequest(document_ref=ref, collection=collection)
            )
            return IngestResult(
                document_id=result.document_id,
                chunks_indexed=result.chunks_indexed,
                collection=result.collection,
            )

    async def query(self, question: str, *, workspace_id: str | None = None, top_k: int = 5) -> QueryResult:
        """Retrieve -> LLM -> Response via the active KnowledgeProvider."""
        with self._telemetry.timed("ai.orchestration.query"):
            result = await self._knowledge_provider.search(
                KnowledgeSearchRequest(query=question, workspace_id=workspace_id, top_k=top_k)
            )
            return QueryResult(
                answer=result.answer,
                context_chunks=result.context_chunks,
                model=result.model,
            )

    async def search(self, question: str, *, workspace_id: str | None = None, top_k: int = 5) -> QueryResult:
        """Alias used by knowledge services and SDK to keep naming explicit."""
        return await self.query(question, workspace_id=workspace_id, top_k=top_k)

    async def sync(self, workspace_id: str, source_type: str, source_uri: str, branch: str | None = None):
        with self._telemetry.timed("ai.orchestration.sync"):
            return await self._knowledge_provider.sync(
                KnowledgeSyncRequest(
                    workspace_id=workspace_id,
                    source_type=source_type,
                    source_uri=source_uri,
                    branch=branch,
                )
            )

    async def delete(self, source_id: str, collection: str = "default") -> None:
        with self._telemetry.timed("ai.orchestration.delete"):
            await self._knowledge_provider.delete(
                KnowledgeDeleteRequest(source_id=source_id, collection=collection)
            )

    async def status(self) -> KnowledgeStatus:
        return await self._knowledge_provider.status()
