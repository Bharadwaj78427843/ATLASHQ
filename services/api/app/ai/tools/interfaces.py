from __future__ import annotations

from typing import Protocol

from app.ai.interfaces.base import HealthCheckResult
from app.ai.tools.models import ToolCallResult, ToolContext, ToolSpec


class Tool(Protocol):
    @property
    def spec(self) -> ToolSpec:
        ...

    async def execute(self, args: dict, context: ToolContext) -> ToolCallResult:
        ...

    async def health(self) -> HealthCheckResult:
        ...
