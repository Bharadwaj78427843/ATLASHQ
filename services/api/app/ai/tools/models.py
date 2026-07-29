from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ToolPermission:
    resource: str
    action: str


@dataclass
class ToolSpec:
    name: str
    description: str
    schema: dict[str, Any] = field(default_factory=dict)
    permissions: list[ToolPermission] = field(default_factory=list)


@dataclass
class ToolContext:
    workspace_id: str | None = None
    organization_id: str | None = None
    user_id: str | None = None
    execution_id: str | None = None


@dataclass
class ToolCallResult:
    tool: str
    ok: bool
    output: Any = None
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
