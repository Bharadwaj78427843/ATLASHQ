from app.ai.skills_runtime.orchestrator import SkillOrchestrator, OrchestrationGraph
from app.ai.skills_runtime.models import SkillExecutionRequest

class OrchestrationPipeline:
    def __init__(self, orchestrator: SkillOrchestrator):
        self._orchestrator = orchestrator

    async def execute_graph(self, graph: OrchestrationGraph, base_request: SkillExecutionRequest):
        return await self._orchestrator.execute_graph(graph, base_request)
