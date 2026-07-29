# Sprint 6 — Operations Guide

## Startup wiring

Application startup performs:

1. Build provider registry with all known providers.
2. Load AI config from defaults + YAML + env + runtime overrides.
3. Activate configured providers for registered categories.
4. Build ProviderFactory.
5. Build KnowledgeProvider via KnowledgeProviderFactory.
6. Build KnowledgeOrchestrator with that provider.
7. Expose SDK + orchestrator + registry in app.state.

## Knowledge service flow

Upload:

1. Persist metadata and file.
2. Queue indexing.
3. Indexing calls orchestrator ingest.
4. Active knowledge provider executes ingest pipeline.

Search:

1. API calls search service.
2. Search service calls orchestrator search.
3. Active knowledge provider executes retrieval + answer generation.

Repository sync:

1. API connects repository source.
2. Service calls orchestrator sync.
3. Provider-specific sync behavior runs.

## Observability hooks

Telemetry spans/counters are emitted around:

- ingest
- extract
- chunk
- embed
- vector upsert
- retrieval
- llm
- sync

Token usage is recorded from LLM responses.

## Test command

Run:

.venv\Scripts\python.exe -m pytest tests\ai -q

Current result after Sprint 6 integration:

- 43 passed
