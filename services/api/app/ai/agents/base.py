"""
app/ai/agents/base.py

Base runtime lifecycle for every AtlasHQ agent.

All concrete agents share these phases:
    initialize -> plan -> execute -> call_tools -> reflect -> finalize
"""
from __future__ import annotations

from abc import abstractmethod
from typing import Any

from app.ai.interfaces.agent import AgentProvider, AgentResult, AgentTask
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.runtime.context import ExecutionContext
from app.ai.runtime.models import ExecutionPlan, PlanStep, StepResult
from app.ai.tools.executor import ToolExecutor
from app.ai.tools.models import ToolContext


class BaseAgent(AgentProvider):
    """Base class for planner and execution agents."""

    provider_name = "base-agent"

    def __init__(self, config: dict | None = None, *, tool_executor: ToolExecutor | None = None) -> None:
        super().__init__(config)
        self._tool_executor = tool_executor

    async def health(self) -> HealthCheckResult:
        status = HealthStatus.HEALTHY if self.is_initialized else HealthStatus.UNKNOWN
        return HealthCheckResult(status=status, message=f"{self.__class__.__name__} is ready.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"agent", "planning", "execution"}))

    async def initialize(self) -> None:
        await super().initialize()

    @abstractmethod
    async def plan(self, context: ExecutionContext) -> ExecutionPlan:
        raise NotImplementedError

    @abstractmethod
    async def execute(self, context: ExecutionContext, plan: ExecutionPlan) -> list[StepResult]:
        raise NotImplementedError

    async def call_tools(self, context: ExecutionContext, tool_name: str, args: dict[str, Any]) -> dict[str, Any]:
        if self._tool_executor is None:
            raise RuntimeError(f"{self.__class__.__name__} cannot call tools without a ToolExecutor")
        result = await self._tool_executor.execute(
            tool_name,
            args,
            ToolContext(
                workspace_id=context.workspace_id,
                organization_id=context.organization_id,
                user_id=context.user_id,
                execution_id=context.execution_id,
            ),
        )
        return {
            "tool": result.tool,
            "ok": result.ok,
            "output": result.output,
            "error": result.error,
            "metadata": result.metadata,
        }

    async def reflect(self, context: ExecutionContext, step_result: StepResult) -> str:
        if step_result.status.value == "failed":
            return f"Step {step_result.step_id} failed: {step_result.error}"
        return f"Step {step_result.step_id} succeeded."

    async def finalize(self, context: ExecutionContext, plan: ExecutionPlan, steps: list[StepResult]) -> str:
        lines = [f"Goal: {plan.goal}"]
        for step in steps:
            status = step.status.value
            if status == "completed":
                lines.append(f"- {step.step_id}: completed")
            else:
                lines.append(f"- {step.step_id}: {status}")
        return "\n".join(lines)

    async def execute_step(self, context: ExecutionContext, step: PlanStep) -> tuple[Any, list[dict[str, Any]]]:
        """Default implementation executes declared step tools in order."""
        evidence: list[dict[str, Any]] = []
        output: Any = None
        for tool in step.tools:
            call = await self.call_tools(context, tool, {"query": step.task})
            evidence.append(call)
            output = call.get("output")
        return output, evidence

    async def run(self, task: AgentTask) -> AgentResult:
        context = ExecutionContext(execution_id="adhoc", prompt=task.goal, metadata=task.metadata)
        plan = await self.plan(context)
        steps = await self.execute(context, plan)
        output = await self.finalize(context, plan, steps)
        return AgentResult(output=output, steps=[])
