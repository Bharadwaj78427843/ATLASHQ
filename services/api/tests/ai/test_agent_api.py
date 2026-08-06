from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.ai.agents.execution_agent import ExecutionAgent
from app.ai.agents.planner_agent import PlannerAgent
from app.ai.config.models import AIConfig
from app.ai.factory.factory import ProviderFactory
from app.ai.knowledge.factory import KnowledgeProviderFactory
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.ai.runtime import AgentRuntime, RuntimeConfig, RuntimeMemoryStore
from app.ai.sdk.sdk import AtlasAISDK
from app.ai.telemetry.hooks import get_telemetry
from app.ai.tools import ToolExecutor, ToolRegistry, build_default_tools
from app.ai.utils.bootstrap import build_default_registry


@asynccontextmanager
async def lifespan(app: FastAPI):
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
    knowledge_provider = KnowledgeProviderFactory(factory, telemetry=telemetry).create()
    orchestrator = KnowledgeOrchestrator(factory, knowledge_provider, telemetry=telemetry)

    memory_provider = await factory.create_memory()
    runtime_memory = RuntimeMemoryStore(memory_provider)

    tool_registry = ToolRegistry()
    runtime_cfg = RuntimeConfig(default_timeout=30)
    for tool in build_default_tools(orchestrator, config={"ai": config.model_dump()}):
        tool_registry.register(tool)
    tool_executor = ToolExecutor(tool_registry)

    planner_agent = PlannerAgent(config={})
    execution_agent = ExecutionAgent(factory=factory, config={}, tool_executor=tool_executor)
    runtime = AgentRuntime(
        planner_agent=planner_agent,
        execution_agent=execution_agent,
        memory_store=runtime_memory,
        config=runtime_cfg,
    )

    sdk = AtlasAISDK(
        registry=registry,
        factory=factory,
        orchestrator=orchestrator,
        telemetry=telemetry,
        runtime=runtime,
        skill_runtime=None,
        tool_registry=tool_registry,
        tool_executor=tool_executor,
        memory_provider=memory_provider,
    )

    app.state.ai_sdk = sdk
    yield
    await registry.shutdown_all()


def test_agent_runtime_endpoints_smoke():
    app = FastAPI(lifespan=lifespan)

    @app.post("/ai/agents/plan")
    async def plan_agent(payload: dict):
        return await app.state.ai_sdk.agents.plan(
            prompt=payload["prompt"],
            workspace_id=payload.get("workspace_id"),
            organization_id=payload.get("organization_id"),
            user_id=payload.get("user_id"),
        )

    @app.post("/ai/agents/execute")
    async def execute_agent(payload: dict):
        return await app.state.ai_sdk.agents.execute(
            prompt=payload["prompt"],
            workspace_id=payload.get("workspace_id"),
            organization_id=payload.get("organization_id"),
            user_id=payload.get("user_id"),
        )

    @app.get("/ai/agents/status/{execution_id}")
    async def status_agent(execution_id: str):
        return await app.state.ai_sdk.agents.status(execution_id)

    @app.get("/ai/tools")
    async def list_tools():
        return await app.state.ai_sdk.tools.list()

    @app.post("/ai/tools/{tool_name}")
    async def execute_tool(tool_name: str, payload: dict):
        return await app.state.ai_sdk.tools.execute(
            tool_name,
            payload.get("args", {}),
            workspace_id=payload.get("workspace_id"),
            organization_id=payload.get("organization_id"),
            user_id=payload.get("user_id"),
            execution_id=payload.get("execution_id"),
        )

    @app.get("/ai/memory")
    async def get_memory(execution_id: str, workspace_id: str | None = None, key: str = "results"):
        return await app.state.ai_sdk.memory.get(workspace_id=workspace_id, execution_id=execution_id, key=key)

    @app.post("/ai/agents/cancel")
    async def cancel_agent(payload: dict):
        return await app.state.ai_sdk.agents.cancel(payload["execution_id"])

    with TestClient(app) as client:
        plan = client.post("/ai/agents/plan", json={"prompt": "Analyze auth", "workspace_id": "w1"})
        assert plan.status_code == 200
        plan_json = plan.json()
        assert "execution_id" in plan_json

        execute = client.post("/ai/agents/execute", json={"prompt": "Analyze auth", "workspace_id": "w1"})
        assert execute.status_code == 200
        execute_json = execute.json()
        assert "execution_id" in execute_json

        status = client.get(f"/ai/agents/status/{execute_json['execution_id']}")
        assert status.status_code == 200

        tools = client.get("/ai/tools")
        assert tools.status_code == 200
        assert "tools" in tools.json()

        tool_exec = client.post(
            "/ai/tools/workspace_tool",
            json={"args": {}, "workspace_id": "w1"},
        )
        assert tool_exec.status_code == 200

        memory = client.get(
            "/ai/memory",
            params={"execution_id": execute_json["execution_id"], "workspace_id": "w1", "key": "results"},
        )
        assert memory.status_code == 200

        cancel = client.post("/ai/agents/cancel", json={"execution_id": execute_json["execution_id"]})
        assert cancel.status_code == 200