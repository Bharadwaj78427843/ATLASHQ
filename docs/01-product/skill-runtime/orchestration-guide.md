# AtlasHQ Orchestration Guide

The `SkillOrchestrator` allows you to execute autonomous AI Engineering graphs using a Directed Acyclic Graph (DAG) pattern.

## Core Concepts

1. **OrchestrationNode**: A node in the DAG. It can be a `SKILL` node, which executes an AI skill, or an `APPROVAL` node, which waits for a human to review the action before continuing.
2. **HandoffProtocol**: The mechanism for mapping outputs from one skill into the required inputs of another skill.
3. **ApprovalGate**: A persistent state machine that blocks DAG execution until a human operator resolves the pending gate.

## Execution Model

- The DAG executes topologically.
- Nodes without dependencies run first.
- If multiple nodes are ready and have `parallelizable: true`, they execute concurrently using `asyncio.gather`.
- The execution state is tracked via the `correlation_id` across the platform.

## Dynamic DAG Generation

AtlasHQ no longer relies on hardcoded workflows. Instead, the **Engineering Manager** skill dynamically parses the user request, identifies dependencies, and generates a JSON DAG on-the-fly. This DAG is then ingested by the `SkillOrchestrator`.

## Resilience & Recovery

- **Node State Tracking:** The orchestrator writes real-time DAG execution state (`PENDING`, `RUNNING`, `COMPLETED`, `FAILED`, `WAITING_APPROVAL`) to the `OrgMemoryProvider`.
- **Automatic Retries:** If a skill node fails, the orchestrator automatically retries up to 2 times.
- **Fallback Human Intervention:** If retries are exhausted, the orchestrator routes the failure to a human approval gate. A human can then inspect the logs and manually approve a retry.

## Human in the Loop (HITL)

AtlasHQ enforces that destructive or high-risk actions require human approval.
This is implemented by placing an `APPROVAL` node as a prerequisite for the risk action.
The DAG halts and the Frontend Execution Dashboard displays the pending approval.

```typescript
const resolveApproval = await aiApi.resolveApproval("gate-123", "APPROVED", "john.doe");
```
