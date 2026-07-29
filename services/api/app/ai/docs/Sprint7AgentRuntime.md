# Sprint 7 - Agent Runtime and Tool Execution Platform

Status: Implemented

This document captures the Sprint 7 backend additions for runtime orchestration, planning/execution, tool plugins, memory integration, and API contracts.

## Scope

- Runtime state machine and execution lifecycle
- Planner and execution agent integration
- Tool plugin framework and default built-in tools
- Runtime memory persistence hooks
- Streaming-ready progress events
- SDK and API expansion without breaking existing chat/knowledge contracts

## Runtime Architecture

Main modules:

- `app/ai/runtime/models.py` - execution request/result and state models
- `app/ai/runtime/state.py` - in-memory execution state tracking
- `app/ai/runtime/events.py` - runtime event types and payload model
- `app/ai/runtime/scheduler.py` - bounded parallel task execution
- `app/ai/runtime/executor.py` - orchestrates step execution and retries
- `app/ai/runtime/memory.py` - runtime memory store abstraction
- `app/ai/runtime/runtime.py` - top-level runtime coordinator

Execution flow:

1. Create `AgentExecutionRequest`
2. Build execution context and emit `planning` event
3. Produce plan via `PlannerAgent`
4. Execute plan via `RuntimeExecutor` + `ExecutionAgent`
5. Persist results in memory and expose status/events

## Tool Framework

Main modules:

- `app/ai/tools/models.py` - tool specification, permission, context, result
- `app/ai/tools/base.py` - base tool contract
- `app/ai/tools/registry.py` - tool registration/discovery
- `app/ai/tools/executor.py` - permission checks and invocation wrapper
- `app/ai/tools/builtin.py` - built-in tools

Built-in tools currently registered on startup:

- `knowledge_search`
- `repository_search`
- `file_tool`
- `github_tool`
- `project_tool`
- `workspace_tool`
- `deployment_tool`
- `configuration_tool`

## Startup and Dependency Wiring

In `app/main.py`, lifespan now wires:

- AI provider registry/config/factory
- Knowledge provider + orchestrator
- Memory provider + `RuntimeMemoryStore`
- Tool registry + default tool set + tool executor
- `PlannerAgent` + `ExecutionAgent`
- `AgentRuntime`
- Extended `AtlasAISDK` with runtime/tool/memory pipelines

Attached to `app.state`:

- `ai_runtime`
- `ai_tool_registry`
- `ai_tool_executor`
- `ai_memory_provider`
- existing AI platform state objects

## SDK Additions

`AtlasAISDK` now includes:

- `sdk.agents` (execute/plan/status/cancel/resume/events)
- `sdk.tools` (list/execute)
- `sdk.memory` (get/clear)

And convenience methods on `AtlasAISDK` for agent operations:

- `execute(...)`
- `plan(...)`
- `status(execution_id)`
- `cancel(execution_id)`
- `resume(execution_id)`

## API Contracts

All routes are under `/api/ai`:

- `POST /agents/execute`
- `POST /agents/plan`
- `GET /agents/status/{execution_id}`
- `GET /agents/events/{execution_id}`
- `POST /agents/cancel`
- `POST /agents/resume`
- `GET /tools`
- `POST /tools/{tool_name}`
- `GET /memory`
- `POST /memory/clear`

Backward compatibility preserved:

- Existing chat, stream, providers, health, and knowledge endpoints remain intact.

## Testing

New Sprint 7 tests:

- `tests/ai/runtime/test_runtime.py`
- `tests/ai/agents/test_planner_agent.py`
- `tests/ai/agents/test_execution_agent.py`
- `tests/ai/tools/test_tool_framework.py`
- `tests/ai/test_agent_api.py`

Validation command used:

```bash
.venv/Scripts/python -m pytest tests/ai tests/test_ai_platform.py
```

Result at implementation time:

- 53 passed
- 0 failed

## Known Follow-ups

- Runtime event persistence is in-memory; consider durable event log for distributed execution.
- Resume behavior is a placeholder and should be upgraded with persisted queues/checkpoints.
- Deprecation warnings from `datetime.utcnow()` remain in runtime state path and can be migrated to timezone-aware UTC in a later hardening pass.
