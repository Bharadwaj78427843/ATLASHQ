"""
app/ai/factory/factory.py

`ProviderFactory` is the single entry point business logic should use to
obtain an active provider for a category. It reads the effective
`AIConfig` and delegates resolution to the `ProviderRegistry` — it never
instantiates a provider class itself.

    factory = ProviderFactory(registry, config)
    llm = await factory.create_llm()

No business logic should construct a provider class directly; everything
flows through here (or through the registry for advanced cases like
runtime provider switching).
"""
from __future__ import annotations

from app.ai.config.models import AIConfig
from app.ai.interfaces.agent import AgentProvider
from app.ai.interfaces.document import DocumentProvider
from app.ai.interfaces.embedding import EmbeddingProvider
from app.ai.interfaces.llm import LLMProvider
from app.ai.interfaces.memory import MemoryProvider
from app.ai.interfaces.prompt import PromptProvider
from app.ai.interfaces.retrieval import RetrievalProvider
from app.ai.interfaces.vectorstore import VectorStoreProvider
from app.ai.registry.registry import ProviderRegistry
from app.ai.registry.types import ProviderCategory


class ProviderFactory:
    """Builds category providers from `AIConfig` via the `ProviderRegistry`."""

    def __init__(self, registry: ProviderRegistry, config: AIConfig) -> None:
        self._registry = registry
        self._config = config

    @property
    def config(self) -> AIConfig:
        return self._config

    def selection_for(self, category: str):
        return self._config.selection_for(category)

    async def _create(self, category: ProviderCategory) -> object:
        selection = self._config.selection_for(category.value)
        return await self._registry.resolve(category, selection.provider, selection.options)

    async def create_llm(self) -> LLMProvider:
        provider = await self._create(ProviderCategory.LLM)
        assert isinstance(provider, LLMProvider)
        return provider

    async def create_retrieval(self) -> RetrievalProvider:
        provider = await self._create(ProviderCategory.RETRIEVAL)
        assert isinstance(provider, RetrievalProvider)
        return provider

    async def create_embeddings(self) -> EmbeddingProvider:
        provider = await self._create(ProviderCategory.EMBEDDING)
        assert isinstance(provider, EmbeddingProvider)
        return provider

    async def create_vectorstore(self) -> VectorStoreProvider:
        provider = await self._create(ProviderCategory.VECTORSTORE)
        assert isinstance(provider, VectorStoreProvider)
        return provider

    async def create_documents(self) -> DocumentProvider:
        provider = await self._create(ProviderCategory.DOCUMENT)
        assert isinstance(provider, DocumentProvider)
        return provider

    async def create_memory(self) -> MemoryProvider:
        provider = await self._create(ProviderCategory.MEMORY)
        assert isinstance(provider, MemoryProvider)
        return provider

    async def create_prompts(self) -> PromptProvider:
        provider = await self._create(ProviderCategory.PROMPT)
        assert isinstance(provider, PromptProvider)
        return provider

    async def create_agents(self) -> AgentProvider:
        provider = await self._create(ProviderCategory.AGENT)
        assert isinstance(provider, AgentProvider)
        return provider
