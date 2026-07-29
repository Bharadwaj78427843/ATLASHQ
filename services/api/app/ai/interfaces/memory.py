"""
app/ai/interfaces/memory.py

Vendor-neutral abstraction for memory providers (conversation, workspace,
agent, long-term). Concrete backends: Redis, Filesystem, ...
"""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.ai.interfaces.base import BaseProvider


@dataclass
class MemoryKey:
    scope: str  # e.g. "conversation" | "workspace" | "agent" | "long-term"
    identifier: str


@dataclass
class MemoryRecord:
    key: MemoryKey
    value: Any
    metadata: dict[str, Any] = field(default_factory=dict)


class MemoryProvider(BaseProvider):
    """Contract for providers that persist conversational/agent state."""

    @abstractmethod
    async def get(self, key: MemoryKey) -> MemoryRecord | None:
        """Return the stored record for `key`, or None if absent."""
        raise NotImplementedError

    @abstractmethod
    async def put(self, record: MemoryRecord) -> None:
        """Persist (or overwrite) a memory record."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, key: MemoryKey) -> None:
        """Remove a single memory record."""
        raise NotImplementedError

    @abstractmethod
    async def clear(self, scope: str) -> None:
        """Remove all records within a scope (e.g. all of one conversation)."""
        raise NotImplementedError
