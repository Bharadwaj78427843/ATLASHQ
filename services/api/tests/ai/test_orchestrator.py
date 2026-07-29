"""
tests/ai/test_orchestrator.py

Sprint 5 — KnowledgeOrchestrator, exercised end-to-end using only mock
providers resolved through the registry/factory. Verifies the pipeline
shape (ingest -> query) without any external calls.
"""
import pytest

from app.ai.config.models import AIConfig
from app.ai.factory.factory import ProviderFactory
from app.ai.interfaces.document import DocumentQuery
from app.ai.knowledge.factory import KnowledgeProviderFactory
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.ai.telemetry.hooks import get_telemetry
from app.ai.utils.bootstrap import build_default_registry


@pytest.fixture
def factory() -> ProviderFactory:
    registry = build_default_registry()
    config = AIConfig(
        knowledge={"provider": "native"},
        documents={"provider": "mock"},
        embeddings={"provider": "mock"},
        vectorstore={"provider": "mock"},
        retrieval={"provider": "mock"},
        llm={"provider": "mock"},
    )
    return ProviderFactory(registry, config)


@pytest.fixture
def orchestrator(factory: ProviderFactory) -> KnowledgeOrchestrator:
    provider = KnowledgeProviderFactory(factory, telemetry=get_telemetry()).create()
    return KnowledgeOrchestrator(factory, provider)


@pytest.mark.asyncio
async def test_ingest_pipeline_indexes_chunks(orchestrator: KnowledgeOrchestrator, factory: ProviderFactory):
    documents = await factory.create_documents()
    refs = await documents.list_documents(DocumentQuery())
    ref = refs[0]

    result = await orchestrator.ingest(ref)
    assert result.document_id == ref.id
    assert result.chunks_indexed >= 1
    assert result.collection == "default"


@pytest.mark.asyncio
async def test_query_pipeline_returns_answer_and_context(orchestrator: KnowledgeOrchestrator):
    result = await orchestrator.query("How do I get started with AtlasHQ?")
    assert result.answer.startswith("[mock-llm]")
    assert len(result.context_chunks) > 0
    assert result.context_chunks[0].content
    assert result.model
