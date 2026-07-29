"""
app/ai/agents/memory_agent.py

Skeleton for agents whose primary job is reading/writing memory on behalf
of other agents. Uses the `MemoryProvider` contract directly (memory
providers are already implemented in Sprint 5, unlike LLM/agent behavior).
"""
from __future__ import annotations

from app.ai.agents.base import BaseAgent
from app.ai.interfaces.agent import AgentResult, AgentTask
from app.ai.interfaces.base import ProviderCapabilities
from app.ai.interfaces.memory import MemoryKey, MemoryProvider, MemoryRecord


class MemoryAgent(BaseAgent):
    """Agent skeleton that wraps a `MemoryProvider` for recall/remember."""

    provider_name = "memory-agent"

    def __init__(self, memory_provider: MemoryProvider, config: dict | None = None) -> None:
        super().__init__(config)
        self._memory = memory_provider

    async def remember(self, scope: str, identifier: str, value: object) -> None:
        await self._memory.put(MemoryRecord(key=MemoryKey(scope=scope, identifier=identifier), value=value))

    async def recall(self, scope: str, identifier: str) -> object | None:
        record = await self._memory.get(MemoryKey(scope=scope, identifier=identifier))
        return record.value if record else None

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"agent", "memory"}), metadata={"skeleton": True})

    async def run(self, task: AgentTask) -> AgentResult:
        raise NotImplementedError(
            "MemoryAgent is a Sprint 5 skeleton; implement run() to make it operational. "
            "remember()/recall() are already usable directly."
        )
