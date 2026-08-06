from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.ai.agents.execution_agent import ExecutionAgent
from app.ai.agents.planner_agent import PlannerAgent
from app.ai.config.models import AIConfig
from app.ai.factory.factory import ProviderFactory
from app.ai.knowledge.factory import KnowledgeProviderFactory
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.ai.runtime import AgentRuntime, RuntimeConfig, RuntimeMemoryStore
from app.ai.sdk.sdk import AtlasAISDK
from app.ai.skills_runtime import SkillExecutionRequest, build_skill_runtime
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
    skill_runtime = await build_skill_runtime(factory, telemetry=telemetry)

    sdk = AtlasAISDK(
        registry=registry,
        factory=factory,
        orchestrator=orchestrator,
        telemetry=telemetry,
        runtime=runtime,
        skill_runtime=skill_runtime,
        tool_registry=tool_registry,
        tool_executor=tool_executor,
        memory_provider=memory_provider,
    )

    app.state.ai_sdk = sdk
    yield
    await registry.shutdown_all()


@pytest.mark.asyncio
async def test_skill_api_smoke():
    app = FastAPI(lifespan=lifespan)

    @app.get("/ai/skills")
    async def list_skills():
        return await app.state.ai_sdk.skills.list()

    @app.get("/ai/skills/{skill_id}")
    async def get_skill(skill_id: str):
        return await app.state.ai_sdk.skills.get(skill_id)

    @app.get("/ai/skills/{skill_id}/schema")
    async def get_skill_schema(skill_id: str):
        return await app.state.ai_sdk.skills.schema(skill_id)

    @app.post("/ai/skills/validate")
    async def validate_skill(payload: dict):
        return await app.state.ai_sdk.skills.validate(skill_id=payload.get("skill_id"), manifest=payload.get("manifest"))

    @app.post("/ai/skills/{skill_id}/execute")
    async def execute_skill(skill_id: str, payload: dict):
        return await app.state.ai_sdk.skills.execute(
            SkillExecutionRequest(
                skill_id=skill_id,
                prompt=payload["prompt"],
                workspace_id=payload.get("workspace_id"),
                policy_context=payload.get("policy_context", {}),
            )
        )

    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            listing = await client.get("/ai/skills")
            assert listing.status_code == 200
            skills = listing.json()["skills"]
            assert any(item.get("registry_entry", {}).get("id") == "engineering_manager" for item in skills)

            detail = await client.get("/ai/skills/engineering_manager")
            assert detail.status_code == 200
            assert detail.json()["skill"]["name"] == "engineering_manager"

            schema = await client.get("/ai/skills/engineering_manager/schema")
            assert schema.status_code == 200
            assert "package" in schema.json()

            validate = await client.post("/ai/skills/validate", json={"skill_id": "engineering_manager"})
            assert validate.status_code == 200
            assert validate.json()["valid"] is True

            execute = await client.post(
                "/ai/skills/engineering_manager/execute",
                json={
                    "prompt": "Prepare Sprint 9 execution plan",
                    "workspace_id": "w1",
                    "policy_context": {"p0_defects": 0, "p1_defects": 0},
                },
            )
            assert execute.status_code == 200
            payload = execute.json()
            assert payload["status"] == "completed"
            assert "outputs" in payload