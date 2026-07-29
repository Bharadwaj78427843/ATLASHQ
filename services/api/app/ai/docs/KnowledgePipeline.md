# AI Platform — Knowledge Pipeline

`KnowledgeOrchestrator` (`app/ai/orchestration/knowledge_orchestrator.py`)
composes providers into the platform's canonical pipeline. It contains
**orchestration only** — no vendor logic, no business rules about what to
index — every stage resolves its provider through `ProviderFactory`.

```
Upload → Extract → Normalize → Chunk → Embed → Index
                                                    ↓
Response ← LLM ← Context Assembly ← Retrieve ←──────┘
```

## Ingest path — `ingest(ref, collection="default")`

| Stage | Provider used | Notes |
|---|---|---|
| Upload | *(caller's responsibility)* | Orchestrator receives a `DocumentRef`, not raw bytes. |
| Extract | `DocumentProvider.fetch()` | Returns raw bytes + best-effort text. |
| Normalize | *(orchestrator, in-process)* | Whitespace collapsing only — real normalization (HTML stripping, OCR, encoding detection) belongs in a document provider. |
| Chunk | `app.ai.utils.chunking.chunk_text()` | Word-count based with overlap; not a retrieval strategy. |
| Embed | `EmbeddingProvider.embed()` | Batched over all chunks. |
| Index | `VectorStoreProvider.upsert()` | Stores `{id, vector, metadata: {document_id, text}}`. |

Returns `IngestResult(document_id, chunks_indexed, collection)`.

## Query path — `query(question, workspace_id=None, top_k=5)`

| Stage | Provider used | Notes |
|---|---|---|
| Retrieve | `RetrievalProvider.retrieve()` | Category-appropriate ranked chunks. |
| Context Assembly | *(orchestrator, in-process)* | Joins chunk contents with a `---` separator. |
| LLM | `LLMProvider.generate()` | System message constrains answers to the assembled context. |
| Response | *(orchestrator)* | Wrapped into `QueryResult(answer, context_chunks, model)`. |

## Telemetry

Every stage is wrapped in `TelemetryContext.timed(name)`
(`app/ai/telemetry/hooks.py`), which records a span + latency metric with
no-op defaults. Token usage is recorded via
`metrics.record_token_usage(provider, prompt_tokens, completion_tokens)`
after each LLM call. Wiring a real tracing/metrics backend means
implementing `TracingHook`/`MetricsHook` and swapping the default
`TelemetryContext` — the orchestrator code does not change.

## What's intentionally NOT here

- No real chunking strategy (semantic, recursive, etc.) — that's a future
  retrieval-provider concern.
- No re-ranking, no hybrid search, no citation extraction.
- No prompt templates hardcoded in the orchestrator — production code
  should resolve prompts via `PromptManager` instead of the inline
  `LLMMessage` literals used here as a Sprint 5 placeholder.
