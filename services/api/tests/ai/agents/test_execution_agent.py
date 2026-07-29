import pytest

from app.ai.agents.execution_agent import ExecutionAgent
from app.ai.agents.planner_agent import PlannerAgent
from app.ai.config.models import AIConfig
from app.ai.factory.factory import ProviderFactory
from app.ai.knowledge.factory import KnowledgeProviderFactory
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.ai.runtime.context import ExecutionContext
from app.ai.telemetry.hooks import get_telemetry
from app.ai.tools import ToolExecutor, ToolRegistry, build_default_tools
from app.ai.utils.bootstrap import build_default_registry


@pytest.mark.asyncio
async def test_execution_agent_executes_plan_steps():
    registry = build_default_registry()
    config = AIConfig(
        knowledge={"provider": "native"},
        documents={"provider": "mock"},
        embeddings={"provider": "mock"},
        vectorstore={"provider": "mock"},
        retrieval={"provider": "mock"},
        llm={"provider": "mock"},
    )
    factory = ProviderFactory(registry, config)
    telemetry = get_telemetry()
    kp = KnowledgeProviderFactory(factory, telemetry=telemetry).create()
    orchestrator = KnowledgeOrchestrator(factory, kp, telemetry=telemetry)

    tools = ToolRegistry()
    for tool in build_default_tools(orchestrator, {"ai": config.model_dump()}):
        tools.register(tool)
    executor = ToolExecutor(tools)

    planner = PlannerAgent(config={})
    agent = ExecutionAgent(factory=factory, config={}, tool_executor=executor)
    context = ExecutionContext(execution_id="e1", prompt="Explain auth", workspace_id="w1")

    plan = await planner.plan(context)
    steps = await agent.execute(context, plan)

    assert len(steps) >= 1
    assert any(s.status.value in {"completed", "failed"} for s in steps)

    summary = await agent.finalize(context, plan, steps)
    assert summary
