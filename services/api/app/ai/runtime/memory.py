from __future__ import annotations

from app.ai.interfaces.memory import MemoryKey, MemoryProvider, MemoryRecord
from app.ai.runtime.context import ExecutionContext


class RuntimeMemoryStore:
    """Runtime memory facade over configured MemoryProvider."""

    def __init__(self, provider: MemoryProvider) -> None:
        self._provider = provider

    def _resolve_identifier(self, context: ExecutionContext) -> str:
        if context.memory_identifier:
            return context.memory_identifier
        if context.memory_scope == "organization":
            return context.organization_id or context.execution_id
        if context.memory_scope == "project":
            return context.project_id or context.workspace_id or context.execution_id
        if context.memory_scope == "session":
            return context.session_id or context.execution_id
        if context.memory_scope == "workspace":
            return context.workspace_id or context.execution_id
        return context.execution_id

    def _key(self, context: ExecutionContext, suffix: str) -> MemoryKey:
        scope = context.memory_scope or "execution"
        identifier = self._resolve_identifier(context)
        return MemoryKey(scope=f"{scope}:{identifier}", identifier=suffix)

    async def append(self, context: ExecutionContext, key: str, value: dict) -> None:
        memory_key = self._key(context, key)
        current = await self._provider.get(memory_key)
        items = list(current.value) if current and isinstance(current.value, list) else []
        items.append(value)
        await self._provider.put(MemoryRecord(key=memory_key, value=items))

    async def write(self, context: ExecutionContext, key: str, value: dict) -> None:
        memory_key = self._key(context, key)
        await self._provider.put(MemoryRecord(key=memory_key, value=value))

    async def read(self, context: ExecutionContext, key: str) -> list[dict]:
        memory_key = self._key(context, key)
        current = await self._provider.get(memory_key)
        if current and isinstance(current.value, list):
            return current.value
        if current and isinstance(current.value, dict):
            return [current.value]
        return []

    async def clear_workspace(self, workspace_id: str) -> None:
        await self._provider.clear(f"workspace:{workspace_id}")
