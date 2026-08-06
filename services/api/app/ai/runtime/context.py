from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class ExecutionContext:
    execution_id: str
    workspace_id: str | None = None
    organization_id: str | None = None
    project_id: str | None = None
    repository_id: str | None = None
    session_id: str | None = None
    user_id: str | None = None
    prompt: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    request_metadata: dict[str, Any] = field(default_factory=dict)
    permissions: dict[str, Any] = field(default_factory=dict)
    memory: dict[str, Any] = field(default_factory=dict)
    model: dict[str, Any] = field(default_factory=dict)
    trace: dict[str, Any] = field(default_factory=dict)
    configuration: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    deadline: datetime | None = None
    cancelled: bool = False
    memory_scope: str = "execution"
    memory_identifier: str | None = None
