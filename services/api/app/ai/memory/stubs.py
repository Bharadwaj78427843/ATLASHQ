"""
app/ai/memory/stubs.py

Lightweight stubs for future memory backends. Each satisfies the
`MemoryProvider` contract but raises `MemoryProviderError` if invoked.
"""
from __future__ import annotations

from app.ai.exceptions.errors import MemoryProviderError
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.memory import MemoryKey, MemoryProvider, MemoryRecord


class _StubMemoryProvider(MemoryProvider):
    def _not_implemented(self) -> MemoryProviderError:
        return MemoryProviderError(
            f"'{self.provider_name}' is a stub provider. Implement its methods to enable it.",
            provider=self.provider_name,
            category="memory",
        )

    async def get(self, key: MemoryKey) -> MemoryRecord | None:
        raise self._not_implemented()

    async def put(self, record: MemoryRecord) -> None:
        raise self._not_implemented()

    async def delete(self, key: MemoryKey) -> None:
        raise self._not_implemented()

    async def clear(self, scope: str) -> None:
        raise self._not_implemented()

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(
            status=HealthStatus.UNKNOWN,
            message=f"'{self.provider_name}' is a stub — not implemented.",
        )

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset(), metadata={"stub": True})

    def validate(self) -> list[str]:
        return [f"'{self.provider_name}' is a stub provider and cannot be used in production."]


class RedisMemoryProvider(_StubMemoryProvider):
    provider_name = "redis"


class FilesystemMemoryProvider(_StubMemoryProvider):
    provider_name = "filesystem"
