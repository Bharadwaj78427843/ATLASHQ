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

    sdk = AtlasAISDK(
        registry=registry,
        factory=factory,
        orchestrator=orchestrator,
        telemetry=telemetry,
        runtime=runtime,
        tool_registry=tool_registry,
        tool_executor=tool_executor,
        memory_provider=memory_provider,
    )
            
    # Attach to app.state
    app.state.ai_registry = registry
    app.state.ai_config = config
    app.state.ai_factory = factory
    app.state.ai_knowledge_provider = knowledge_provider
    app.state.ai_orchestrator = orchestrator
    app.state.ai_runtime = runtime
    app.state.ai_tool_registry = tool_registry
    app.state.ai_tool_executor = tool_executor
    app.state.ai_memory_provider = memory_provider
    app.state.ai_prompt_manager = prompt_manager
    app.state.ai_sdk = sdk
    app.state.ai_telemetry = telemetry

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

app.include_router(health.router)
app.include_router(auth_router.router)
app.include_router(orgs_router.router)
app.include_router(org_members_router.router)
app.include_router(workspaces_router.router)
app.include_router(projects_router.router)
app.include_router(environments_router.router)
app.include_router(knowledge_router.router)
app.include_router(ai_router.router)
