from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import health
from app.routers import auth as auth_router
from app.routers import organizations as orgs_router
from app.routers import organization_members as org_members_router
from app.routers import workspaces as workspaces_router
from app.routers import projects as projects_router
from app.routers import environments as environments_router
from app.routers import knowledge as knowledge_router
from app.routers import ai as ai_router
from app.routers import skills as skills_router
from app.routers import ai_orchestration
from app.routers import ai_approvals
from app.routers import ai_memory

from contextlib import asynccontextmanager
from app.ai.config.loader import load_ai_config
from app.ai.factory.factory import ProviderFactory
from app.ai.agents.execution_agent import ExecutionAgent
from app.ai.agents.planner_agent import PlannerAgent
from app.ai.knowledge.factory import KnowledgeProviderFactory
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.ai.runtime import AgentRuntime, RuntimeConfig, RuntimeMemoryStore
from app.ai.telemetry.hooks import get_telemetry
from app.ai.prompts.manager import PromptManager
from app.ai.sdk.sdk import AtlasAISDK
from app.ai.tools import ToolExecutor, ToolRegistry, build_default_tools
from app.ai.utils.bootstrap import activate_from_config, build_default_registry
from app.ai.skills_runtime import build_skill_runtime
from app.ai.skills_runtime.orchestrator import SkillOrchestrator
from app.ai.skills_runtime.approval import ApprovalGate
from app.ai.skills_runtime.handoff import HandoffProtocol


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Bootstrap AI Platform ---
    registry = build_default_registry()
    config = load_ai_config()
    activate_from_config(registry, config)

    factory = ProviderFactory(registry=registry, config=config)
    telemetry = get_telemetry()
    knowledge_provider = KnowledgeProviderFactory(factory, telemetry=telemetry).create()
    orchestrator = KnowledgeOrchestrator(
        factory=factory,
        knowledge_provider=knowledge_provider,
        telemetry=telemetry,
    )
    from app.ai.prompts.providers import FilesystemPromptProvider
    prompt_provider = FilesystemPromptProvider(config=config.prompts.options)
    prompt_manager = PromptManager(provider=prompt_provider)

    memory_provider = await factory.create_memory()
    runtime_memory = RuntimeMemoryStore(memory_provider)

    tool_registry = ToolRegistry()
    runtime_cfg = RuntimeConfig(
        default_agent=config.runtime.default_agent,
        enable_streaming=config.runtime.enable_streaming,
        enable_memory=config.runtime.enable_memory,
        enable_planner=config.runtime.enable_planner,
        max_parallel_tasks=config.runtime.max_parallel_tasks,
        max_tool_retries=config.runtime.max_tool_retries,
        default_timeout=config.runtime.default_timeout,
    )
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

    skill_runtime = await build_skill_runtime(factory, telemetry=telemetry, memory_provider=memory_provider)

    handoff_protocol = HandoffProtocol()
    approval_gate = ApprovalGate()
    skill_orchestrator = SkillOrchestrator(
        skill_runtime=skill_runtime,
        handoff_protocol=handoff_protocol,
        approval_gate=approval_gate,
        telemetry=telemetry,
        memory_provider=memory_provider
    )

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
        skill_orchestrator=skill_orchestrator,
        approval_gate=approval_gate
    )

    # Attach to app.state
    app.state.ai_registry = registry
    app.state.ai_config = config
    app.state.ai_factory = factory
    app.state.ai_knowledge_provider = knowledge_provider
    app.state.ai_orchestrator = orchestrator
    app.state.ai_runtime = runtime
    app.state.ai_skill_runtime = skill_runtime
    app.state.ai_tool_registry = tool_registry
    app.state.ai_tool_executor = tool_executor
    app.state.ai_memory_provider = memory_provider
    app.state.ai_prompt_manager = prompt_manager
    app.state.ai_sdk = sdk
    app.state.ai_telemetry = telemetry
    app.state.ai_skill_orchestrator = skill_orchestrator

    yield

    # Teardown
    await registry.shutdown_all()


app = FastAPI(title="Atlas API", version="0.1.0", lifespan=lifespan)

# Add CORS middleware just in case frontend needs it from browser, though server components don't strictly need it.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ROUTERS = [
    health.router,
    auth_router.router,
    orgs_router.router,
    org_members_router.router,
    workspaces_router.router,
    projects_router.router,
    environments_router.router,
    knowledge_router.router,
    ai_router.router,
    skills_router.router,
    ai_orchestration.router,
    ai_approvals.router,
    ai_memory.router,
]

# Primary routes consumed by the frontend proxy.
for router in ROUTERS:
    app.include_router(router)

# Backward-compatible API namespace for tests and legacy clients.
for router in ROUTERS:
    app.include_router(router, prefix="/api")
