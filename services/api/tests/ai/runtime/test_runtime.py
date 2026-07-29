import pytest

from app.ai.agents.execution_agent import ExecutionAgent
from app.ai.agents.planner_agent import PlannerAgent
from app.ai.config.models import AIConfig
from app.ai.factory.factory import ProviderFactory
from app.ai.runtime import AgentRuntime, RuntimeConfig, RuntimeMemoryStore
from app.ai.runtime.models import AgentExecutionRequest, ExecutionStatus
from app.ai.tools import ToolExecutor, ToolRegistry, build_default_tools
from app.ai.utils.bootstrap import build_default_registry
from app.ai.knowledge.factory import KnowledgeProviderFactory
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.ai.telemetry.hooks import get_telemetry


@pytest.mark.asyncio
async def test_runtime_execute_and_status():
    registry = build_default_registry()
    config = AIConfig(
        knowledge={"provider": "native"},
        documents={"provider": "mock"},
        embeddings={"provider": "mock"},
        vectorstore={"provider": "mock"},
        retrieval={"provider": "mock"},
        llm={"provider": "mock"},
        memory={"provider": "mock"},
    )
    factory = ProviderFactory(registry, config)
    telemetry = get_telemetry()
    kp = KnowledgeProviderFactory(factory, telemetry=telemetry).create()
    orchestrator = KnowledgeOrchestrator(factory, kp, telemetry=telemetry)
    memory_provider = await factory.create_memory()
    memory_store = RuntimeMemoryStore(memory_provider)
    tool_registry = ToolRegistry()
    for tool in build_default_tools(orchestrator, {"ai": config.model_dump()}):
        tool_registry.register(tool)
    tool_executor = ToolExecutor(tool_registry)
    planner = PlannerAgent(config={})
    executor = ExecutionAgent(factory=factory, config={}, tool_executor=tool_executor)
    runtime = AgentRuntime(
        planner_agent=planner,
        execution_agent=executor,
        memory_store=memory_store,
        config=RuntimeConfig(default_timeout=30),
    )

    result = await runtime.execute(AgentExecutionRequest(prompt="Analyze authentication", workspace_id="w1"))
    assert result.status in {ExecutionStatus.COMPLETED, ExecutionStatus.FAILED}
    status = runtime.status(result.execution_id)
    assert status["execution_id"] == result.execution_id


@pytest.mark.asyncio
async def test_runtime_cancel():
    registry = build_default_registry()
    config = AIConfig(
        knowledge={"provider": "native"},
        documents={"provider": "mock"},
        embeddings={"provider": "mock"},
        vectorstore={"provider": "mock"},
        retrieval={"provider": "mock"},
        llm={"provider": "mock"},
        memory={"provider": "mock"},
    )
    factory = ProviderFactory(registry, config)
    telemetry = get_telemetry()
    kp = KnowledgeProviderFactory(factory, telemetry=telemetry).create()
    orchestrator = KnowledgeOrchestrator(factory, kp, telemetry=telemetry)
    memory_provider = await factory.create_memory()
    memory_store = RuntimeMemoryStore(memory_provider)
    tool_registry = ToolRegistry()
    for tool in build_default_tools(orchestrator, {"ai": config.model_dump()}):
        tool_registry.register(tool)
    tool_executor = ToolExecutor(tool_registry)
    planner = PlannerAgent(config={})
    executor = ExecutionAgent(factory=factory, config={}, tool_executor=tool_executor)
    runtime = AgentRuntime(
        planner_agent=planner,
        execution_agent=executor,
        memory_store=memory_store,
        config=RuntimeConfig(default_timeout=30),
    )

    execution_id, _ = await runtime.plan(AgentExecutionRequest(prompt="Plan only", workspace_id="w1"))
    cancelled = runtime.cancel(execution_id)
    assert cancelled["status"] == "cancelled"
    assert runtime.status(execution_id)["status"] == "cancelled"
