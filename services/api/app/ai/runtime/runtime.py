from __future__ import annotations

import asyncio
import uuid
from dataclasses import asdict

from app.ai.runtime.context import ExecutionContext
from app.ai.runtime.events import RuntimeEvent, RuntimeEventType
from app.ai.runtime.executor import RuntimeExecutor
from app.ai.runtime.interfaces import EventPublisher
from app.ai.runtime.memory import RuntimeMemoryStore
from app.ai.runtime.models import AgentExecutionRequest, AgentExecutionResult, ExecutionPlan, ExecutionStatus, RuntimeConfig
from app.ai.runtime.scheduler import RuntimeScheduler
from app.ai.runtime.state import ExecutionState


class InMemoryEventPublisher:
    def __init__(self) -> None:
        self._events: dict[str, list[RuntimeEvent]] = {}

    async def publish(self, event: RuntimeEvent) -> None:
        self._events.setdefault(event.execution_id, []).append(event)

    def events(self, execution_id: str) -> list[RuntimeEvent]:
        return self._events.get(execution_id, [])


class AgentRuntime:
    def __init__(self, *, planner_agent, execution_agent, memory_store: RuntimeMemoryStore, config: RuntimeConfig) -> None:
        self._planner = planner_agent
        self._executor_agent = execution_agent
        self._memory = memory_store
        self._config = config
        self._publisher = InMemoryEventPublisher()
        self._scheduler = RuntimeScheduler(max_parallel_tasks=config.max_parallel_tasks)
        self._executor = RuntimeExecutor(
            event_publisher=self._publisher,
            scheduler=self._scheduler,
            max_tool_retries=config.max_tool_retries,
        )
        self._states: dict[str, ExecutionState] = {}
        self._results: dict[str, AgentExecutionResult] = {}

    async def plan(self, request: AgentExecutionRequest) -> tuple[str, ExecutionPlan]:
        execution_id = str(uuid.uuid4())
        context = ExecutionContext(
            execution_id=execution_id,
            workspace_id=request.workspace_id,
            organization_id=request.organization_id,
            user_id=request.user_id,
            prompt=request.prompt,
            metadata=request.metadata,
        )
        self._states[execution_id] = ExecutionState(execution_id=execution_id, status=ExecutionStatus.QUEUED)
        await self._publisher.publish(RuntimeEvent(execution_id, RuntimeEventType.PLANNING, "Planning execution"))
        plan = await self._planner.plan(context)
        await self._memory.append(context, "plans", {"goal": plan.goal, "step_count": len(plan.steps)})
        return execution_id, plan

    async def execute(self, request: AgentExecutionRequest) -> AgentExecutionResult:
        execution_id, plan = await self.plan(request)
        state = self._states[execution_id]
        state.set_status(ExecutionStatus.RUNNING)

        context = ExecutionContext(
            execution_id=execution_id,
            workspace_id=request.workspace_id,
            organization_id=request.organization_id,
            user_id=request.user_id,
            prompt=request.prompt,
            metadata=request.metadata,
        )

        timeout = request.timeout_seconds or self._config.default_timeout
        try:
            result = await self._executor.execute(context, plan, self._executor_agent, timeout_seconds=timeout)
            state.set_status(result.status)
            self._results[execution_id] = result
            await self._memory.append(context, "results", {"status": result.status.value, "answer": result.answer})
            await self._publisher.publish(RuntimeEvent(execution_id, RuntimeEventType.COMPLETED, "Execution completed"))
            return result
        except Exception as exc:  # noqa: BLE001
            state.set_status(ExecutionStatus.FAILED)
            state.error = str(exc)
            failed = AgentExecutionResult(execution_id=execution_id, status=ExecutionStatus.FAILED, error=str(exc))
            self._results[execution_id] = failed
            await self._publisher.publish(RuntimeEvent(execution_id, RuntimeEventType.ERROR, str(exc)))
            return failed

    def status(self, execution_id: str) -> dict:
        state = self._states.get(execution_id)
        if not state:
            return {"execution_id": execution_id, "status": "not_found"}
        result = self._results.get(execution_id)
        return {
            "execution_id": execution_id,
            "status": state.status.value,
            "error": state.error,
            "result": asdict(result) if result else None,
        }

    def cancel(self, execution_id: str) -> dict:
        self._executor.cancel(execution_id)
        state = self._states.get(execution_id)
        if state:
            state.set_status(ExecutionStatus.CANCELLED)
        return {"execution_id": execution_id, "status": ExecutionStatus.CANCELLED.value}

    def events(self, execution_id: str) -> list[dict]:
        return [asdict(event) for event in self._publisher.events(execution_id)]

    async def memory(self, workspace_id: str | None, execution_id: str, key: str) -> list[dict]:
        context = ExecutionContext(execution_id=execution_id, workspace_id=workspace_id)
        return await self._memory.read(context, key)
