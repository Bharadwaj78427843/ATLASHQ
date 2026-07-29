"""
tests/ai/test_factory.py

Sprint 5 — ProviderFactory builds providers from AIConfig via the registry,
never by importing a concrete provider class itself.
"""
import pytest

from app.ai.config.models import AIConfig
from app.ai.factory.factory import ProviderFactory
from app.ai.interfaces.embedding import EmbeddingProvider
from app.ai.interfaces.llm import LLMProvider
from app.ai.interfaces.memory import MemoryProvider
from app.ai.interfaces.retrieval import RetrievalProvider
from app.ai.interfaces.vectorstore import VectorStoreProvider
from app.ai.utils.bootstrap import build_default_registry


@pytest.fixture
def factory() -> ProviderFactory:
    registry = build_default_registry()
    config = AIConfig()  # all defaults -> "mock"
    return ProviderFactory(registry, config)


@pytest.mark.asyncio
async def test_create_llm_returns_llm_provider(factory: ProviderFactory):
    llm = await factory.create_llm()
    assert isinstance(llm, LLMProvider)
    health = await llm.health()
    assert health.status.value == "healthy"


@pytest.mark.asyncio
async def test_create_retrieval_returns_retrieval_provider(factory: ProviderFactory):
    provider = await factory.create_retrieval()
    assert isinstance(provider, RetrievalProvider)


@pytest.mark.asyncio
async def test_create_embeddings_returns_embedding_provider(factory: ProviderFactory):
    provider = await factory.create_embeddings()
    assert isinstance(provider, EmbeddingProvider)


@pytest.mark.asyncio
async def test_create_vectorstore_returns_vectorstore_provider(factory: ProviderFactory):
    provider = await factory.create_vectorstore()
    assert isinstance(provider, VectorStoreProvider)


@pytest.mark.asyncio
async def test_create_memory_returns_memory_provider(factory: ProviderFactory):
    provider = await factory.create_memory()
    assert isinstance(provider, MemoryProvider)


@pytest.mark.asyncio
async def test_factory_reuses_registry_cache(factory: ProviderFactory):
    first = await factory.create_llm()
    second = await factory.create_llm()
    assert first is second


@pytest.mark.asyncio
async def test_swapping_config_provider_changes_resolution():
    registry = build_default_registry()
    mock_config = AIConfig()
    stub_config = AIConfig(llm={"provider": "anthropic"})

    mock_factory = ProviderFactory(registry, mock_config)
    stub_factory = ProviderFactory(registry, stub_config)

    mock_llm = await mock_factory.create_llm()
    stub_llm = await stub_factory.create_llm()

    assert mock_llm.provider_name == "mock"
    assert stub_llm.provider_name == "anthropic"
    assert mock_llm is not stub_llm
