from typing import Any
from app.ai.factory.factory import ProviderFactory
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator, IngestResult
from app.ai.telemetry.hooks import TelemetryContext
from app.ai.interfaces.document import DocumentRef


class KnowledgePipeline:
    def __init__(
        self,
        factory: ProviderFactory,
        orchestrator: KnowledgeOrchestrator,
        telemetry: TelemetryContext,
    ):
        self._factory = factory
        self._orchestrator = orchestrator
        self._telemetry = telemetry

    async def search(self, query: str, workspace_id: str | None = None, top_k: int = 5) -> dict[str, Any]:
        with self._telemetry.timed("sdk.knowledge.search"):
            result = await self._orchestrator.search(query, workspace_id=workspace_id, top_k=top_k)

            return {
                "answer": result.answer,
                "results": [
                    {
                        "content": chunk.content,
                        "score": chunk.score,
                        "filename": chunk.metadata.get("filename", "unknown"),
                        "metadata": chunk.metadata,
                    }
                    for chunk in result.context_chunks
                ],
                "model": result.model,
            }

    async def upload(self, document_id: str, collection: str = "default") -> dict[str, Any]:
        with self._telemetry.timed("sdk.knowledge.upload"):
            ref = DocumentRef(id=document_id, name="uploaded_file", uri=f"file://{document_id}", mime_type="text/plain")
            result: IngestResult = await self._orchestrator.ingest(ref, collection=collection)
            return {
                "document_id": result.document_id,
                "chunks_indexed": result.chunks_indexed,
                "collection": result.collection
            }

    async def sync(self, workspace_id: str, source_type: str, source_uri: str, branch: str | None = None) -> dict[str, Any]:
        with self._telemetry.timed("sdk.knowledge.sync"):
            result = await self._orchestrator.sync(
                workspace_id=workspace_id,
                source_type=source_type,
                source_uri=source_uri,
                branch=branch,
            )
            return {
                "status": result.status,
                "provider": result.provider,
                "details": result.details,
            }

    async def status(self) -> dict[str, Any]:
        status = await self._orchestrator.status()
        return {
            "provider": status.provider,
            "status": status.status,
            "details": status.details,
        }
