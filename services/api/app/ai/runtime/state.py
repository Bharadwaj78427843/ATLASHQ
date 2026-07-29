from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from app.ai.runtime.models import ExecutionStatus


@dataclass
class ExecutionState:
    execution_id: str
    status: ExecutionStatus = ExecutionStatus.QUEUED
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    retries: int = 0
    error: str | None = None

    def set_status(self, status: ExecutionStatus) -> None:
        self.status = status
        self.updated_at = datetime.utcnow()
