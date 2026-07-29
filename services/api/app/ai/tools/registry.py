from __future__ import annotations

from app.ai.tools.exceptions import ToolNotFoundError
from app.ai.tools.models import ToolSpec


class ToolRegistry:
    def __init__(self) -> None:
        self._tools: dict[str, object] = {}

    def register(self, tool) -> None:
        self._tools[tool.spec.name] = tool

    def get(self, name: str):
        tool = self._tools.get(name)
        if tool is None:
            raise ToolNotFoundError(f"Tool '{name}' is not registered")
        return tool

    def list_specs(self) -> list[ToolSpec]:
        return [tool.spec for tool in self._tools.values()]

    async def health(self) -> dict[str, str]:
        result = {}
        for tool in self._tools.values():
            health = await tool.health()
            result[tool.spec.name] = health.status.value
        return result
