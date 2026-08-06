from app.ai.factory.factory import ProviderFactory
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.ai.registry.registry import ProviderRegistry
from app.ai.telemetry.hooks import TelemetryContext

from .agents import AgentPipeline
from .chat import ChatPipeline
from .health import SystemHealth
from .knowledge import KnowledgePipeline
from .memory import MemoryPipeline
from .providers import ProviderListing
from .skills import SkillsPipeline
from .tools import ToolPipeline
from .orchestration import OrchestrationPipeline
from .approvals import ApprovalsPipeline


class AtlasAISDK:
    """
    The main facade for the Atlas AI Platform.
    This SDK acts as the sole public entry point for business logic to access
    AI capabilities, hiding the complexity of registries, factories, and
    orchestration layers.
    """

    def __init__(
        self,
        registry: ProviderRegistry,
        factory: ProviderFactory,
        orchestrator: KnowledgeOrchestrator,
        telemetry: TelemetryContext,
        runtime,
        skill_runtime,
        tool_registry,
        tool_executor,
        memory_provider,
        skill_orchestrator,
        approval_gate
    ):
        self._registry = registry
        self._factory = factory
        self._orchestrator = orchestrator
        self._telemetry = telemetry

        self.chat = ChatPipeline(factory, orchestrator, telemetry)
        self.knowledge = KnowledgePipeline(factory, orchestrator, telemetry)
        self.health = SystemHealth(registry)
        self.providers = ProviderListing(registry)
        self.agents = AgentPipeline(runtime)
        self.skills = SkillsPipeline(skill_runtime)
        self.tools = ToolPipeline(tool_registry, tool_executor)
        self.memory = MemoryPipeline(runtime, memory_provider)
        self.orchestration = OrchestrationPipeline(skill_orchestrator)
        self.approvals = ApprovalsPipeline(approval_gate)

    async def execute(self, **kwargs):
        return await self.agents.execute(**kwargs)

    async def plan(self, **kwargs):
        return await self.agents.plan(**kwargs)

    async def status(self, execution_id: str):
        return await self.agents.status(execution_id)

    async def cancel(self, execution_id: str):
        return await self.agents.cancel(execution_id)