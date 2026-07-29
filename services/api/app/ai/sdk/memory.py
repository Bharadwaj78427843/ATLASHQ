from __future__ import annotations


class MemoryPipeline:
    def __init__(self, runtime, memory_provider) -> None:
        self._runtime = runtime
        self._memory_provider = memory_provider

    async def get(self, workspace_id: str | None, execution_id: str, key: str = "results") -> dict:
        items = await self._runtime.memory(workspace_id, execution_id, key)
        return {"workspace_id": workspace_id, "execution_id": execution_id, "key": key, "items": items}

    async def clear(self, scope: str) -> dict:
        await self._memory_provider.clear(scope)
        return {"scope": scope, "status": "cleared"}
