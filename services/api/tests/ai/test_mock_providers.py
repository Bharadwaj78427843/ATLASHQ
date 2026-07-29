"""
tests/ai/test_mock_providers.py

Sprint 5 — every mock provider is a fully functional, zero-external-call
implementation of its interface. These tests instantiate mocks directly
(mocks are the one provider kind it's fine to construct in tests, since
the goal here is to verify the mock's own behavior in isolation).
"""
import pytest

from app.ai.documents.mock import MockDocumentProvider
from app.ai.embeddings.mock import MockEmbeddingProvider
from app.ai.interfaces.base import HealthStatus
from app.ai.interfaces.document import DocumentQuery
from app.ai.interfaces.embedding import EmbeddingRequest
from app.ai.interfaces.llm import LLMMessage, LLMRequest
from app.ai.interfaces.memory import MemoryKey, MemoryRecord
from app.ai.interfaces.prompt import PromptTemplate
from app.ai.interfaces.retrieval import RetrievalQuery
from app.ai.interfaces.vectorstore import VectorQuery, VectorRecord
from app.ai.llm.mock import MockLLMProvider
from app.ai.memory.mock import MockMemoryProvider
from app.ai.retrieval.mock import MockRetrievalProvider
from app.ai.vectorstores.mock import MockVectorStoreProvider


@pytest.mark.asyncio
async def test_mock_llm_provider():
    provider = MockLLMProvider()
    await provider.initialize()
    response = await provider.generate(LLMRequest(messages=[LLMMessage(role="user", content="hello")]))
    assert "hello" in response.content
    assert (await provider.health()).status == HealthStatus.HEALTHY
    assert provider.capabilities().supports("chat")
    await provider.shutdown()
    assert not provider.is_initialized


@pytest.mark.asyncio
async def test_mock_retrieval_provider():
    provider = MockRetrievalProvider()
    await provider.initialize()
    result = await provider.retrieve(RetrievalQuery(text="how do I invite a teammate?", top_k=2))
    assert len(result.chunks) == 2
    assert (await provider.health()).status == HealthStatus.HEALTHY


@pytest.mark.asyncio
async def test_mock_embedding_provider_is_deterministic():
    provider = MockEmbeddingProvider()
    await provider.initialize()
    response_a = await provider.embed(EmbeddingRequest(inputs=["hello world"]))
    response_b = await provider.embed(EmbeddingRequest(inputs=["hello world"]))
    assert response_a.vectors == response_b.vectors
    assert len(response_a.vectors[0]) == response_a.dimensions


@pytest.mark.asyncio
async def test_mock_vectorstore_provider_upsert_query_delete():
    provider = MockVectorStoreProvider()
    await provider.initialize()
    await provider.upsert(
        "default",
        [
            VectorRecord(id="a", vector=[1.0, 0.0]),
            VectorRecord(id="b", vector=[0.0, 1.0]),
        ],
    )
    matches = await provider.query("default", VectorQuery(vector=[1.0, 0.0], top_k=1))
    assert matches[0].id == "a"

    await provider.delete("default", ["a"])
    matches = await provider.query("default", VectorQuery(vector=[1.0, 0.0], top_k=5))
    assert all(m.id != "a" for m in matches)


@pytest.mark.asyncio
async def test_mock_document_provider_list_and_fetch():
    provider = MockDocumentProvider()
    await provider.initialize()
    docs = await provider.list_documents(DocumentQuery())
    assert len(docs) >= 1
    content = await provider.fetch(docs[0])
    assert content.text and docs[0].name in content.text


@pytest.mark.asyncio
async def test_mock_memory_provider_put_get_delete_clear():
    provider = MockMemoryProvider()
    await provider.initialize()
    key = MemoryKey(scope="conversation", identifier="conv-1")

    assert await provider.get(key) is None
    await provider.put(MemoryRecord(key=key, value={"messages": ["hi"]}))
    record = await provider.get(key)
    assert record is not None
    assert record.value == {"messages": ["hi"]}

    await provider.delete(key)
    assert await provider.get(key) is None

    await provider.put(MemoryRecord(key=key, value="x"))
    await provider.clear("conversation")
    assert await provider.get(key) is None


def test_prompt_template_render_requires_all_variables():
    template = PromptTemplate(
        name="greeting", namespace="default", version="v1",
        template="Hello {name}!", variables=["name"],
    )
    assert template.render(name="Ada") == "Hello Ada!"
    with pytest.raises(KeyError):
        template.render()
