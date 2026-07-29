from typing import Any
import asyncio
from app.ai.factory.factory import ProviderFactory
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator, QueryResult
from app.ai.telemetry.hooks import TelemetryContext


class ChatPipeline:
    def __init__(
        self,
        factory: ProviderFactory,
        orchestrator: KnowledgeOrchestrator,
        telemetry: TelemetryContext,
    ):
        self._factory = factory
        self._orchestrator = orchestrator
        self._telemetry = telemetry

    async def chat(self, prompt: str, workspace_id: str | None = None) -> dict[str, Any]:
        """
        Main entry point for chat requests.
        Routes through the knowledge orchestrator for full RAG support.
        """
        with self._telemetry.timed("sdk.chat"):
            # Simple orchestration query which does retrieval + LLM
            result: QueryResult = await self._orchestrator.query(prompt, workspace_id=workspace_id)
            
            return {
                "response": result.answer,
                "context_used": len(result.context_chunks) > 0,
                "model": result.model,
                "chunks": [chunk.content for chunk in result.context_chunks]
            }

    async def chat_stream(self, prompt: str, workspace_id: str | None = None):
        """Yields incremental chunks for SSE without changing chat contract."""
        response = await self.chat(prompt=prompt, workspace_id=workspace_id)
        text = response["response"]
        for token in text.split(" "):
            yield token + " "
            await asyncio.sleep(0)
