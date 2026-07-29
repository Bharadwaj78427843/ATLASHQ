from __future__ import annotations

from dataclasses import asdict

from app.ai.interfaces.memory import MemoryKey, MemoryProvider, MemoryRecord
from app.ai.runtime.context import ExecutionContext


class RuntimeMemoryStore:
    """Runtime memory facade over configured MemoryProvider."""

    def __init__(self, provider: MemoryProvider) -> None:
        self._provider = provider

    def _key(self, context: ExecutionContext, suffix: str) -> MemoryKey:
        workspace = context.workspace_id or "global"
        execution = context.execution_id
        return MemoryKey(scope=suffix, identifier=f"{workspace}:{execution}")

    async def append(self, context: ExecutionContext, key: str, value: dict) -> None:
        memory_key = self._key(context, key)
        current = await self._provider.get(memory_key)
        items = list(current.value) if current and isinstance(current.value, list) else []
        items.append(value)
        await self._provider.put(MemoryRecord(key=memory_key, value=items))

    async def read(self, context: ExecutionContext, key: str) -> list[dict]:
        memory_key = self._key(context, key)
        current = await self._provider.get(memory_key)
        if current and isinstance(current.value, list):
            return current.value
        return []

    async def clear_workspace(self, workspace_id: str) -> None:
        await self._provider.clear(f"workspace:{workspace_id}")
