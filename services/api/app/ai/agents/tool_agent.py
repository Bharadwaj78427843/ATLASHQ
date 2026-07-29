"""
app/ai/agents/tool_agent.py

Shared mixin-like agent for tool registration and invocation.
"""
from __future__ import annotations

from app.ai.agents.base import BaseAgent
from app.ai.interfaces.base import ProviderCapabilities
from app.ai.tools.executor import ToolExecutor
from app.ai.tools.registry import ToolRegistry


class ToolAgent(BaseAgent):
    """Agent that owns a tool registry/executor and can invoke named tools."""

    provider_name = "tool-agent"

    def __init__(self, config: dict | None = None, *, tool_registry: ToolRegistry | None = None, **kwargs) -> None:
        self._tool_registry = tool_registry or ToolRegistry()
        self._tool_executor = ToolExecutor(self._tool_registry)
        super().__init__(config=config, tool_executor=self._tool_executor, **kwargs)

    def register_tool(self, tool) -> None:
        self._tool_registry.register(tool)

    def available_tools(self) -> list[str]:
        return sorted([spec.name for spec in self._tool_registry.list_specs()])

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            features=frozenset({"agent", "tools"}),
            metadata={"registered_tools": self.available_tools()},
        )
