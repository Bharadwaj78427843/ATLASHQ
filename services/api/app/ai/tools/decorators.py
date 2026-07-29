from __future__ import annotations

from app.ai.tools.models import ToolPermission, ToolSpec


def tool(name: str, description: str, schema: dict | None = None, permissions: list[ToolPermission] | None = None):
    def wrapper(cls):
        cls.TOOL_SPEC = ToolSpec(
            name=name,
            description=description,
            schema=schema or {},
            permissions=permissions or [],
        )
        return cls

    return wrapper
