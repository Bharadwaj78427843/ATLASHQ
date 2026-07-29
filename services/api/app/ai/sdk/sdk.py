import time
from typing import Any

from app.ai.factory.factory import ProviderFactory
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.ai.registry.registry import ProviderRegistry
from app.ai.registry.types import ProviderCategory
from app.ai.telemetry.hooks import TelemetryContext
from app.ai.interfaces.document import DocumentRef

from .chat import ChatPipeline
from .knowledge import KnowledgePipeline
from .health import SystemHealth
from .providers import ProviderListing
from .agents import AgentPipeline
from .tools import ToolPipeline
from .memory import MemoryPipeline


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
        tool_registry,
        tool_executor,
        memory_provider,
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
        self.tools = ToolPipeline(tool_registry, tool_executor)
        self.memory = MemoryPipeline(runtime, memory_provider)

    async def execute(self, **kwargs):
        return await self.agents.execute(**kwargs)

    async def plan(self, **kwargs):
        return await self.agents.plan(**kwargs)

    async def status(self, execution_id: str):
        return await self.agents.status(execution_id)

    async def cancel(self, execution_id: str):
        return await self.agents.cancel(execution_id)

    async def resume(self, execution_id: str):
        return await self.agents.resume(execution_id)
