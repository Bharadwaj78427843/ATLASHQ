from __future__ import annotations

from typing import Protocol

from app.ai.runtime.context import ExecutionContext
from app.ai.runtime.events import RuntimeEvent
from app.ai.runtime.models import AgentExecutionResult, ExecutionPlan, PlanStep


class Planner(Protocol):
    async def plan(self, context: ExecutionContext) -> ExecutionPlan:
        ...


class Executor(Protocol):
    async def execute(self, context: ExecutionContext, plan: ExecutionPlan) -> AgentExecutionResult:
        ...


class EventPublisher(Protocol):
    async def publish(self, event: RuntimeEvent) -> None:
        ...


class RuntimeMemory(Protocol):
    async def append(self, context: ExecutionContext, key: str, value: dict) -> None:
        ...

    async def read(self, context: ExecutionContext, key: str) -> list[dict]:
        ...
