import pytest

from app.ai.config.models import AIConfig
from app.ai.factory.factory import ProviderFactory
from app.ai.knowledge.factory import KnowledgeProviderFactory
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.ai.telemetry.hooks import get_telemetry
from app.ai.tools import ToolExecutor, ToolRegistry, build_default_tools
from app.ai.tools.models import ToolContext
from app.ai.utils.bootstrap import build_default_registry


@pytest.mark.asyncio
async def test_tool_registry_and_listing():
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

    specs = tools.list_specs()
    names = [spec.name for spec in specs]
    assert "knowledge_search" in names
    assert "repository_search" in names


@pytest.mark.asyncio
async def test_tool_execution_and_permission_validation():
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

    ok = await executor.execute("workspace_tool", {}, ToolContext(workspace_id="w1"))
    assert ok.ok

    with pytest.raises(Exception):
        await executor.execute("workspace_tool", {}, ToolContext())
