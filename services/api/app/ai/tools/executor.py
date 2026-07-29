from __future__ import annotations

from app.ai.tools.exceptions import ToolExecutionError, ToolPermissionError
from app.ai.tools.models import ToolCallResult, ToolContext
from app.ai.tools.registry import ToolRegistry


class ToolExecutor:
    def __init__(self, registry: ToolRegistry) -> None:
        self._registry = registry

    def _validate_permissions(self, tool, context: ToolContext) -> None:
        for permission in tool.spec.permissions:
            if permission.resource == "workspace" and not context.workspace_id:
                raise ToolPermissionError(f"Tool '{tool.spec.name}' requires workspace context")
            if permission.resource == "organization" and not context.organization_id:
                raise ToolPermissionError(f"Tool '{tool.spec.name}' requires organization context")

    async def execute(self, tool_name: str, args: dict, context: ToolContext) -> ToolCallResult:
        tool = self._registry.get(tool_name)
        self._validate_permissions(tool, context)
        try:
            return await tool.execute(args, context)
        except Exception as exc:  # noqa: BLE001
            raise ToolExecutionError(f"Tool '{tool_name}' execution failed: {exc}") from exc
