from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.interfaces.base import HealthCheckResult, HealthStatus
from app.ai.tools.models import ToolCallResult, ToolContext, ToolSpec


class BaseTool(ABC):
    def __init__(self, spec: ToolSpec) -> None:
        self._spec = spec

    @property
    def spec(self) -> ToolSpec:
        return self._spec

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.HEALTHY, message=f"{self.spec.name} ready")

    @abstractmethod
    async def execute(self, args: dict, context: ToolContext) -> ToolCallResult:
        raise NotImplementedError
