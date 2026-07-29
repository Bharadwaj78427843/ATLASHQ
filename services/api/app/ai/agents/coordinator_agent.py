"""
app/ai/agents/coordinator_agent.py

Skeleton for agents that coordinate a set of sub-agents (e.g. a planner
handing steps to one or more execution agents). Dispatch/aggregation logic
is left for a future sprint.
"""
from __future__ import annotations

from app.ai.agents.base import BaseAgent
from app.ai.interfaces.agent import AgentProvider, AgentResult, AgentTask
from app.ai.interfaces.base import ProviderCapabilities


class CoordinatorAgent(BaseAgent):
    """Agent skeleton that owns a set of sub-agents to delegate work to."""

    provider_name = "coordinator-agent"

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)
        self._sub_agents: dict[str, AgentProvider] = {}

    def register_agent(self, name: str, agent: AgentProvider) -> None:
        self._sub_agents[name] = agent

    def sub_agents(self) -> list[str]:
        return sorted(self._sub_agents)

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            features=frozenset({"agent", "coordination"}),
            metadata={"skeleton": True, "sub_agents": self.sub_agents()},
        )

    async def run(self, task: AgentTask) -> AgentResult:
        raise NotImplementedError(
            "CoordinatorAgent is a Sprint 5 skeleton; implement dispatch/aggregation to make it operational."
        )
