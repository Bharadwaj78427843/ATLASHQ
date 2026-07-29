"""
app/ai/interfaces/agent.py

Vendor-neutral abstraction for agent providers. An "agent provider" is the
runnable unit the orchestration layer invokes; concrete agent behaviors
live under `app/ai/agents/` and implement this contract.
"""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.ai.interfaces.base import BaseProvider


@dataclass
class AgentTask:
    goal: str
    context: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentStep:
    name: str
    output: Any = None


@dataclass
class AgentResult:
    output: Any
    steps: list[AgentStep] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


class AgentProvider(BaseProvider):
    """Contract for providers that run an agent task to completion."""

    @abstractmethod
    async def run(self, task: AgentTask) -> AgentResult:
        """Execute `task` and return the final result."""
        raise NotImplementedError
