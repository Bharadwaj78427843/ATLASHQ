from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ExecutionContext:
    execution_id: str
    workspace_id: str | None = None
    organization_id: str | None = None
    user_id: str | None = None
    prompt: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
