"""
app/ai/memory/mock.py

In-memory memory provider (process-local dict) used for local development
and tests. Backs conversation, workspace, agent, and long-term scopes
uniformly — a scope is just a namespace within `MemoryKey`.
"""
from __future__ import annotations

from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.memory import MemoryKey, MemoryProvider, MemoryRecord


class MockMemoryProvider(MemoryProvider):
    provider_name = "mock"

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)
        self._store: dict[tuple[str, str], MemoryRecord] = {}

    def _key(self, key: MemoryKey) -> tuple[str, str]:
        return (key.scope, key.identifier)

    async def get(self, key: MemoryKey) -> MemoryRecord | None:
        return self._store.get(self._key(key))

    async def put(self, record: MemoryRecord) -> None:
        self._store[self._key(record.key)] = record

    async def delete(self, key: MemoryKey) -> None:
        self._store.pop(self._key(key), None)

    async def clear(self, scope: str) -> None:
        for key in [k for k in self._store if k[0] == scope]:
            self._store.pop(key, None)

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.HEALTHY, message="Mock memory provider is always healthy.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            features=frozenset({"conversation", "workspace", "agent", "long-term"})
        )
