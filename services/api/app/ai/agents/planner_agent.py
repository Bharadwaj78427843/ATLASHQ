"""
app/ai/agents/planner_agent.py

Planner agent that decomposes prompts into structured execution plans.
"""
from __future__ import annotations

from app.ai.agents.base import BaseAgent
from app.ai.runtime.context import ExecutionContext
from app.ai.runtime.models import ExecutionPlan, PlanStep, StepResult


class PlannerAgent(BaseAgent):
    """Turns natural language requests into execution plans."""

    provider_name = "planner-agent"

    async def plan(self, context: ExecutionContext) -> ExecutionPlan:
        text = context.prompt.lower()

        steps: list[PlanStep] = [
            PlanStep(
                id="step-1",
                task="Search repository for relevant implementation",
                priority=1,
                dependencies=[],
                expected_output="Matching files and code references",
                estimated_cost=0.01,
                tools=["repository_search"],
            ),
            PlanStep(
                id="step-2",
                task="Search workspace knowledge for context",
                priority=2,
                dependencies=["step-1"],
                expected_output="Relevant knowledge snippets",
                estimated_cost=0.01,
                tools=["knowledge_search"],
            ),
            PlanStep(
                id="step-3",
                task="Read configuration relevant to requested domain",
                priority=3,
                dependencies=["step-1"],
                expected_output="Config settings and constraints",
                estimated_cost=0.005,
                tools=["configuration_tool"],
                parallelizable=True,
            ),
            PlanStep(
                id="step-4",
                task="Synthesize findings and summarize",
                priority=4,
                dependencies=["step-2", "step-3"],
                expected_output="Grounded summary",
                estimated_cost=0.02,
                tools=[],
            ),
        ]

        if "deploy" in text or "release" in text:
            steps.insert(
                2,
                PlanStep(
                    id="step-2b",
                    task="Check deployment state",
                    priority=2,
                    dependencies=["step-1"],
                    expected_output="Deployment health/status",
                    estimated_cost=0.01,
                    tools=["deployment_tool"],
                ),
            )

        return ExecutionPlan(goal=context.prompt, steps=steps, metadata={"workspace_id": context.workspace_id})

    async def execute(self, context: ExecutionContext, plan: ExecutionPlan) -> list[StepResult]:
        # Planner does not execute tools; it returns planned steps only.
        return []
