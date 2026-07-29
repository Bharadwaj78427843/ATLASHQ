from __future__ import annotations

from app.ai.factory.factory import ProviderFactory
from app.ai.interfaces.base import HealthCheckResult, HealthStatus
from app.ai.interfaces.embedding import EmbeddingRequest
from app.ai.interfaces.llm import LLMMessage, LLMRequest
from app.ai.interfaces.retrieval import RetrievalQuery
from app.ai.interfaces.vectorstore import VectorRecord
from app.ai.knowledge.base import KnowledgeProvider
from app.ai.knowledge.models import (
    KnowledgeDeleteRequest,
    KnowledgeIngestRequest,
    KnowledgeIngestResult,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
    KnowledgeSearchResultChunk,
    KnowledgeStatus,
    KnowledgeSyncRequest,
    KnowledgeSyncResult,
)
from app.ai.telemetry.hooks import TelemetryContext, get_telemetry
from app.ai.utils.chunking import chunk_text


class NativeKnowledgeProvider(KnowledgeProvider):
    provider_name = "native"

    def __init__(self, factory: ProviderFactory, telemetry: TelemetryContext | None = None) -> None:
        self._factory = factory
        self._telemetry = telemetry or get_telemetry()

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.HEALTHY, message="Native knowledge provider ready.")

    async def ingest(self, request: KnowledgeIngestRequest) -> KnowledgeIngestResult:
        with self._telemetry.timed("ai.knowledge.native.ingest"):
            documents = await self._factory.create_documents()
            with self._telemetry.timed("ai.knowledge.native.extract"):
                content = await documents.fetch(request.document_ref)

            text = " ".join((content.text or content.content.decode("utf-8", errors="ignore")).split())
            with self._telemetry.timed("ai.knowledge.native.chunk"):
                chunks = chunk_text(text)

            if not chunks:
                return KnowledgeIngestResult(
                    document_id=request.document_ref.id,
                    chunks_indexed=0,
                    collection=request.collection,
                    provider=self.provider_name,
                )

            embeddings = await self._factory.create_embeddings()
            with self._telemetry.timed("ai.knowledge.native.embed"):
                embedded = await embeddings.embed(EmbeddingRequest(inputs=chunks))

            vectorstore = await self._factory.create_vectorstore()
            records = [
                VectorRecord(
                    id=f"{request.document_ref.id}-{i}",
                    vector=vector,
                    metadata={"document_id": request.document_ref.id, "text": chunk, **request.metadata},
                )
                for i, (chunk, vector) in enumerate(zip(chunks, embedded.vectors))
            ]

            with self._telemetry.timed("ai.knowledge.native.vector.upsert"):
                await vectorstore.upsert(request.collection, records)

            return KnowledgeIngestResult(
                document_id=request.document_ref.id,
                chunks_indexed=len(records),
                collection=request.collection,
                provider=self.provider_name,
            )

    async def search(self, request: KnowledgeSearchRequest) -> KnowledgeSearchResult:
        with self._telemetry.timed("ai.knowledge.native.search"):
            retrieval = await self._factory.create_retrieval()
            with self._telemetry.timed("ai.knowledge.native.retrieve"):
                result = await retrieval.retrieve(
                    RetrievalQuery(
                        text=request.query,
                        workspace_id=request.workspace_id,
                        top_k=request.top_k,
                        filters=request.filters,
                    )
                )

            llm = await self._factory.create_llm()
            context = "\n---\n".join(chunk.content for chunk in result.chunks)
            llm_request = LLMRequest(
                messages=[
                    LLMMessage(role="system", content="Answer using only the provided context."),
                    LLMMessage(role="user", content=f"Context:\n{context}\n\nQuestion: {request.query}"),
                ]
            )
            with self._telemetry.timed("ai.knowledge.native.llm"):
                response = await llm.generate(llm_request)

            self._telemetry.metrics.record_token_usage(
                llm.provider_name,
                response.usage.prompt_tokens,
                response.usage.completion_tokens,
                tags={"knowledge_provider": self.provider_name},
            )

            return KnowledgeSearchResult(
                answer=response.content,
                context_chunks=[
                    KnowledgeSearchResultChunk(
                        id=chunk.id,
                        content=chunk.content,
                        score=chunk.score,
                        metadata=chunk.metadata,
                    )
                    for chunk in result.chunks
                ],
                model=response.model,
                provider=self.provider_name,
            )

    async def delete(self, request: KnowledgeDeleteRequest) -> None:
        vectorstore = await self._factory.create_vectorstore()
        with self._telemetry.timed("ai.knowledge.native.delete"):
            await vectorstore.delete(request.collection, [request.source_id])

    async def sync(self, request: KnowledgeSyncRequest) -> KnowledgeSyncResult:
        with self._telemetry.timed("ai.knowledge.native.sync"):
            return KnowledgeSyncResult(
                status="queued",
                provider=self.provider_name,
                details={
                    "source_type": request.source_type,
                    "source_uri": request.source_uri,
                    "branch": request.branch,
                },
            )

    async def status(self) -> KnowledgeStatus:
        return KnowledgeStatus(provider=self.provider_name, status="ready")
