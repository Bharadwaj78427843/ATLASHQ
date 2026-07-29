import pytest

from app.ai.agents.planner_agent import PlannerAgent
from app.ai.runtime.context import ExecutionContext


@pytest.mark.asyncio
async def test_planner_generates_structured_plan():
    planner = PlannerAgent(config={})
    context = ExecutionContext(execution_id="e1", prompt="Analyze authentication flow", workspace_id="w1")
    plan = await planner.plan(context)

    assert plan.goal == "Analyze authentication flow"
    assert len(plan.steps) >= 4
    assert plan.steps[0].task
    assert isinstance(plan.steps[0].estimated_cost, float)
    assert isinstance(plan.steps[0].dependencies, list)
