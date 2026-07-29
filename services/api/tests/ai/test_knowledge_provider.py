import pytest

from app.ai.config.models import AIConfig
from app.ai.factory.factory import ProviderFactory
from app.ai.interfaces.document import DocumentQuery
from app.ai.knowledge.factory import KnowledgeProviderFactory
from app.ai.knowledge.models import (
    KnowledgeIngestRequest,
    KnowledgeSearchRequest,
    KnowledgeSyncRequest,
)
from app.ai.telemetry.hooks import get_telemetry
from app.ai.utils.bootstrap import build_default_registry


@pytest.mark.asyncio
async def test_native_provider_ingest_and_search_with_mocks():
    registry = build_default_registry()
    config = AIConfig(
        knowledge={"provider": "native"},
        documents={"provider": "mock"},
        embeddings={"provider": "mock"},
        vectorstore={"provider": "mock"},
        retrieval={"provider": "mock"},
        llm={"provider": "mock"},
    )
    factory = ProviderFactory(registry, config)
    provider = KnowledgeProviderFactory(factory, telemetry=get_telemetry()).create()

    docs = await factory.create_documents()
    ref = (await docs.list_documents(DocumentQuery()))[0]

    ingest = await provider.ingest(KnowledgeIngestRequest(document_ref=ref, collection="test"))
    assert ingest.provider == "native"
    assert ingest.chunks_indexed >= 1

    result = await provider.search(KnowledgeSearchRequest(query="hello", workspace_id="w1", top_k=3))
    assert result.provider == "native"
    assert result.answer.startswith("[mock-llm]")
    assert result.context_chunks


@pytest.mark.asyncio
async def test_ragflow_provider_sync_and_status_via_stubbed_requests(monkeypatch):
    registry = build_default_registry()
    config = AIConfig(
        knowledge={
            "provider": "ragflow",
            "options": {
                "base_url": "https://ragflow.example",
                "api_key": "token",
                "endpoints": {
                    "health": "api/health",
                    "status": "api/status",
                    "upload_document": "api/doc/upload",
                    "upload_repository": "api/repo/upload",
                    "search": "api/search",
                    "delete_dataset": "api/dataset/delete",
                },
            },
        }
    )
    factory = ProviderFactory(registry, config)
    provider = KnowledgeProviderFactory(factory, telemetry=get_telemetry()).create()

    async def fake_request(method, endpoint_key, json=None):
        if endpoint_key == "health":
            return {"status": "ok"}
        if endpoint_key == "status":
            return {"status": "ready", "datasets": 2}
        if endpoint_key == "upload_repository":
            return {"status": "queued", "job_id": "job-1"}
        if endpoint_key == "search":
            return {
                "answer": "grounded answer",
                "model": "ragflow-llm",
                "results": [{"id": "c1", "content": "ctx", "score": 0.9, "metadata": {}}],
            }
        return {}

    monkeypatch.setattr(provider, "_request", fake_request)

    health = await provider.health()
    assert health.status.value == "healthy"

    sync = await provider.sync(
        KnowledgeSyncRequest(
            workspace_id="w1",
            source_type="repository",
            source_uri="github://owner/repo",
            branch="main",
        )
    )
    assert sync.status == "queued"

    status = await provider.status()
    assert status.status == "ready"

    search = await provider.search(KnowledgeSearchRequest(query="q"))
    assert search.answer == "grounded answer"
    assert search.context_chunks[0].content == "ctx"
