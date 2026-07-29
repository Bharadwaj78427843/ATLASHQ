"""
app/ai/utils/bootstrap.py

Wires every known provider implementation into a `ProviderRegistry` using
lazy (`module_path`) registration — importing this module never imports a
single vendor SDK. The registry only imports a provider's module the first
time that specific provider is resolved.

This is the ONE place that knows every provider that exists. It contains
no business logic and makes no decisions about which provider is active;
that comes from `AIConfig` (see `app/ai/config`).
"""
from __future__ import annotations

from app.ai.registry.registry import ProviderRegistry
from app.ai.registry.types import ProviderCategory

_CAT = ProviderCategory


def build_default_registry() -> ProviderRegistry:
    """Return a fresh `ProviderRegistry` with every known provider registered."""
    registry = ProviderRegistry()

    # ── LLM ────────────────────────────────────────────────────────────────
    registry.register(_CAT.LLM, "mock", module_path="app.ai.llm.mock:MockLLMProvider")
    registry.register(_CAT.LLM, "azure-openai", module_path="app.ai.llm.stubs:AzureOpenAIProvider")
    registry.register(_CAT.LLM, "openai", module_path="app.ai.llm.openai_provider:OpenAILLMProvider")
    registry.register(_CAT.LLM, "anthropic", module_path="app.ai.llm.stubs:AnthropicProvider")
    registry.register(_CAT.LLM, "gemini", module_path="app.ai.llm.stubs:GeminiProvider")
    registry.register(_CAT.LLM, "ollama", module_path="app.ai.llm.stubs:OllamaProvider")
    registry.register(_CAT.LLM, "lm-studio", module_path="app.ai.llm.stubs:LMStudioProvider")
    registry.register(_CAT.LLM, "openrouter", module_path="app.ai.llm.stubs:OpenRouterProvider")

    # ── Retrieval ────────────────────────────────────────────────────────
    registry.register(_CAT.RETRIEVAL, "mock", module_path="app.ai.retrieval.mock:MockRetrievalProvider")
    registry.register(_CAT.RETRIEVAL, "ragflow", module_path="app.ai.retrieval.ragflow:RAGFlowProvider")

    # ── Embeddings ───────────────────────────────────────────────────────
    registry.register(_CAT.EMBEDDING, "mock", module_path="app.ai.embeddings.mock:MockEmbeddingProvider")
    registry.register(_CAT.EMBEDDING, "openai", module_path="app.ai.embeddings.openai_provider:OpenAIEmbeddingProvider")
    registry.register(_CAT.EMBEDDING, "azure", module_path="app.ai.embeddings.stubs:AzureEmbeddingProvider")
    registry.register(
        _CAT.EMBEDDING, "sentence-transformers", module_path="app.ai.embeddings.stubs:SentenceTransformersProvider"
    )
    registry.register(_CAT.EMBEDDING, "voyageai", module_path="app.ai.embeddings.stubs:VoyageAIProvider")
    registry.register(_CAT.EMBEDDING, "ollama", module_path="app.ai.embeddings.stubs:OllamaEmbeddingProvider")

    # ── Vector store ─────────────────────────────────────────────────────
    registry.register(_CAT.VECTORSTORE, "mock", module_path="app.ai.vectorstores.mock:MockVectorStoreProvider")
    registry.register(_CAT.VECTORSTORE, "pgvector", module_path="app.ai.vectorstores.stubs:PgVectorProvider")
    registry.register(_CAT.VECTORSTORE, "qdrant", module_path="app.ai.vectorstores.qdrant:QdrantVectorStoreProvider")
    registry.register(_CAT.VECTORSTORE, "weaviate", module_path="app.ai.vectorstores.stubs:WeaviateProvider")
    registry.register(_CAT.VECTORSTORE, "pinecone", module_path="app.ai.vectorstores.stubs:PineconeProvider")
    registry.register(_CAT.VECTORSTORE, "milvus", module_path="app.ai.vectorstores.stubs:MilvusProvider")
    registry.register(_CAT.VECTORSTORE, "redis-vector", module_path="app.ai.vectorstores.stubs:RedisVectorProvider")

    # ── Documents ────────────────────────────────────────────────────────
    registry.register(_CAT.DOCUMENT, "mock", module_path="app.ai.documents.mock:MockDocumentProvider")
    registry.register(_CAT.DOCUMENT, "filesystem", module_path="app.ai.documents.filesystem:FilesystemDocumentProvider")
    registry.register(_CAT.DOCUMENT, "github", module_path="app.ai.documents.stubs:GitHubDocumentProvider")
    registry.register(_CAT.DOCUMENT, "gitlab", module_path="app.ai.documents.stubs:GitLabDocumentProvider")
    registry.register(
        _CAT.DOCUMENT, "azure-devops", module_path="app.ai.documents.stubs:AzureDevOpsDocumentProvider"
    )
    registry.register(_CAT.DOCUMENT, "sharepoint", module_path="app.ai.documents.stubs:SharePointDocumentProvider")
    registry.register(_CAT.DOCUMENT, "confluence", module_path="app.ai.documents.stubs:ConfluenceDocumentProvider")
    registry.register(_CAT.DOCUMENT, "s3", module_path="app.ai.documents.stubs:S3DocumentProvider")
    registry.register(
        _CAT.DOCUMENT, "google-drive", module_path="app.ai.documents.stubs:GoogleDriveDocumentProvider"
    )
    registry.register(_CAT.DOCUMENT, "onedrive", module_path="app.ai.documents.stubs:OneDriveDocumentProvider")

    # ── Memory ───────────────────────────────────────────────────────────
    registry.register(_CAT.MEMORY, "mock", module_path="app.ai.memory.mock:MockMemoryProvider")
    registry.register(_CAT.MEMORY, "redis", module_path="app.ai.memory.stubs:RedisMemoryProvider")
    registry.register(_CAT.MEMORY, "filesystem", module_path="app.ai.memory.stubs:FilesystemMemoryProvider")

    # ── Prompts ──────────────────────────────────────────────────────────
    registry.register(_CAT.PROMPT, "filesystem", module_path="app.ai.prompts.providers:FilesystemPromptProvider")
    registry.register(_CAT.PROMPT, "database", module_path="app.ai.prompts.providers:DatabasePromptProvider")

    # ── Agents ───────────────────────────────────────────────────────────
    # Concrete agent kinds are skeletons (see app/ai/agents/); no default
    # "mock" agent provider is registered yet because AgentProvider.run()
    # has no meaningful no-op behavior to fall back to.

    return registry


def activate_from_config(registry: ProviderRegistry, config) -> None:  # config: AIConfig
    """Mark each category's configured provider as active on `registry`."""
    for category in ProviderCategory:
        if category.value == "knowledge":
            continue
        selection = config.selection_for(category.value)
        if registry.is_registered(category, selection.provider):
            registry.set_active(category, selection.provider)
