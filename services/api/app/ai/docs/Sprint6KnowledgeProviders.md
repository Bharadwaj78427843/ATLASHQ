# Sprint 6 — Production Knowledge Providers

## What changed

Sprint 6 keeps the Sprint 5 architecture and replaces mock-only flows with
production-ready provider integrations while preserving interfaces:

- Knowledge abstraction introduced under `app/ai/knowledge/`.
- `KnowledgeOrchestrator` now delegates to `KnowledgeProvider`.
- Native and RAGFlow pipelines are both first-class and selected by config.
- OpenAI LLM + embeddings and Qdrant vector store providers are implemented.

## Provider selection

Use `ai.knowledge.provider` in AI config:

- `native`
- `ragflow`
- `mock` (routes to native behavior with mock downstream providers)

No SDK business logic changes are required when switching providers.

## Environment variables

Supported aliases:

- KNOWLEDGE_PROVIDER
- LLM_PROVIDER
- VECTOR_PROVIDER
- EMBED_PROVIDER
- OPENAI_API_KEY
- OPENAI_MODEL
- OPENAI_EMBED_MODEL
- RAGFLOW_BASE_URL
- RAGFLOW_API_KEY
- QDRANT_URL
- QDRANT_API_KEY

Also supported with full path mapping:

- ATLAS_AI__...

## RAGFlow endpoint configuration

RAGFlow endpoint paths are loaded from configuration at:

- ai.knowledge.options.endpoints

Expected keys:

- health
- status
- upload_document
- upload_repository
- search
- delete_dataset

No endpoint paths are hardcoded in provider logic.

## API additions

- POST /api/ai/chat/stream
- POST /api/ai/knowledge/sync
- GET /api/ai/knowledge/status

These endpoints are additive and do not break existing Ask Atlas flows.
