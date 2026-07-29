"""
app/ai/agents/execution_agent.py

Execution agent that runs structured plans by calling registered tools
and synthesizing a grounded final response.
"""
from __future__ import annotations

from app.ai.agents.base import BaseAgent
from app.ai.factory.factory import ProviderFactory
from app.ai.interfaces.llm import LLMMessage, LLMRequest
from app.ai.runtime.context import ExecutionContext
from app.ai.runtime.models import ExecutionPlan, StepResult, StepStatus


class ExecutionAgent(BaseAgent):
    """Executes plan steps, collecting tool evidence and producing final output."""

    provider_name = "execution-agent"

    def __init__(self, factory: ProviderFactory, config: dict | None = None, **kwargs) -> None:
        super().__init__(config=config, **kwargs)
        self._factory = factory

    async def plan(self, context: ExecutionContext) -> ExecutionPlan:
        return ExecutionPlan(goal=context.prompt, steps=[])

    async def execute(self, context: ExecutionContext, plan: ExecutionPlan) -> list[StepResult]:
        results: list[StepResult] = []
        for step in plan.steps:
            try:
                output, evidence = await self.execute_step(context, step)
                results.append(
                    StepResult(
                        step_id=step.id,
                        status=StepStatus.COMPLETED,
                        output=output,
                        evidence=evidence,
                    )
                )
            except Exception as exc:  # noqa: BLE001
                results.append(StepResult(step_id=step.id, status=StepStatus.FAILED, error=str(exc)))
        return results

    async def finalize(self, context: ExecutionContext, plan: ExecutionPlan, steps: list[StepResult]) -> str:
        completed = [s for s in steps if s.status == StepStatus.COMPLETED]
        failed = [s for s in steps if s.status == StepStatus.FAILED]

        evidence_lines = []
        for step in completed:
            evidence_lines.append(f"Step {step.step_id}: {step.output}")
        if failed:
            evidence_lines.append("Failures:")
            evidence_lines.extend([f"- {s.step_id}: {s.error}" for s in failed])

        llm = await self._factory.create_llm()
        response = await llm.generate(
            LLMRequest(
                messages=[
                    LLMMessage(role="system", content="Generate a grounded response using provided execution evidence."),
                    LLMMessage(
                        role="user",
                        content=f"Goal: {plan.goal}\n\nEvidence:\n" + "\n".join(evidence_lines),
                    ),
                ]
            )
        )
        return response.content
