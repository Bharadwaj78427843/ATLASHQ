# AI Platform — Provider Guide

Each provider category is a contract in `app/ai/interfaces/` plus a home
package under `app/ai/<category>/` for implementations. This guide lists
every category, its contract, and its current implementations.

| Category | Interface | Package | Mock | Stubs |
|---|---|---|---|---|
| LLM | `LLMProvider` | `app/ai/llm/` | `MockLLMProvider` | azure-openai, openai, anthropic, gemini, ollama, lm-studio, openrouter |
| Retrieval | `RetrievalProvider` | `app/ai/retrieval/` | `MockRetrievalProvider` | ragflow |
| Embeddings | `EmbeddingProvider` | `app/ai/embeddings/` | `MockEmbeddingProvider` | openai, azure, sentence-transformers, voyageai, ollama |
| Vector Store | `VectorStoreProvider` | `app/ai/vectorstores/` | `MockVectorStoreProvider` | pgvector, qdrant, weaviate, pinecone, milvus, redis-vector |
| Documents | `DocumentProvider` | `app/ai/documents/` | `MockDocumentProvider` | filesystem, github, gitlab, azure-devops, sharepoint, confluence, s3, google-drive, onedrive |
| Memory | `MemoryProvider` | `app/ai/memory/` | `MockMemoryProvider` | redis, filesystem |
| Prompts | `PromptProvider` | `app/ai/prompts/` | — | `FilesystemPromptProvider` (implemented), `DatabasePromptProvider` (stub) |
| Agents | `AgentProvider` | `app/ai/agents/` | — | `BaseAgent`/`ToolAgent`/`PlannerAgent`/`ExecutionAgent`/`CoordinatorAgent`/`MemoryAgent` skeletons only |

## Every provider implements `BaseProvider`

```python
class BaseProvider(ABC):
    async def initialize(self) -> None: ...
    async def shutdown(self) -> None: ...
    async def health(self) -> HealthCheckResult: ...      # abstract
    def capabilities(self) -> ProviderCapabilities: ...    # abstract
    def validate(self) -> list[str]: ...
    def configuration(self) -> dict: ...
```

- `initialize()` / `shutdown()` — lifecycle hooks called once by the
  registry around first use / teardown. Idempotent.
- `health()` — must never raise; returns `HEALTHY` / `DEGRADED` /
  `UNHEALTHY` / `UNKNOWN` with a message.
- `capabilities()` — declares supported features (e.g. `"streaming"`) so
  callers can branch on capability, not on provider identity.
- `validate()` — returns a list of configuration problems (empty = valid).
  Stub providers always return a non-empty list.
- `configuration()` — returns a redacted view of the active config
  (keys containing `secret`/`key` are stripped).

## Stub providers

Every vendor listed in the mission brief that isn't implemented yet has a
**stub**: a class that satisfies its interface, registers normally, reports
`HealthStatus.UNKNOWN` with a "stub — not implemented" message, and raises
a category-specific error (e.g. `LLMError`) if an action method is called.
This lets the platform register/discover/resolve every known provider
today, while making it obvious (via `health()`/`validate()`) that a stub
isn't production-ready.

## Mock providers

Mocks are fully functional, in-memory implementations with **zero external
calls**, used for local development and tests:

- `MockLLMProvider` echoes the last user message.
- `MockRetrievalProvider` returns canned chunks.
- `MockEmbeddingProvider` hashes text into a deterministic vector.
- `MockVectorStoreProvider` is an in-memory cosine-similarity store.
- `MockDocumentProvider` serves two fixture documents.
- `MockMemoryProvider` is an in-memory dict keyed by `(scope, identifier)`.

## Choosing a provider

Providers are selected entirely by configuration — see
[Configuration.md](Configuration.md). Business logic calls
`ProviderFactory.create_llm()` (etc.), never `MockLLMProvider()` or
`AzureOpenAIProvider()` directly.
