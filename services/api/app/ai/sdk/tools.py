from __future__ import annotations


class ToolPipeline:
    def __init__(self, tool_registry, tool_executor) -> None:
        self._tool_registry = tool_registry
        self._tool_executor = tool_executor

    async def list(self) -> dict:
        return {
            "tools": [
                {
                    "name": spec.name,
                    "description": spec.description,
                    "schema": spec.schema,
                    "permissions": [{"resource": p.resource, "action": p.action} for p in spec.permissions],
                }
                for spec in self._tool_registry.list_specs()
            ]
        }

    async def execute(self, tool_name: str, args: dict, *, workspace_id: str | None, organization_id: str | None, user_id: str | None, execution_id: str | None = None) -> dict:
        from app.ai.tools.models import ToolContext

        result = await self._tool_executor.execute(
            tool_name,
            args,
            ToolContext(
                workspace_id=workspace_id,
                organization_id=organization_id,
                user_id=user_id,
                execution_id=execution_id,
            ),
        )
        return {
            "tool": result.tool,
            "ok": result.ok,
            "output": result.output,
            "error": result.error,
            "metadata": result.metadata,
        }
