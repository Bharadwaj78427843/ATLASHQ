from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class RuntimeEventType(str, Enum):
    PLANNING = "planning"
    STEP_STARTED = "step_started"
    TOOL_STARTED = "tool_started"
    TOOL_COMPLETED = "tool_completed"
    STEP_COMPLETED = "step_completed"
    WAITING = "waiting"
    ERROR = "error"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


@dataclass
class RuntimeEvent:
    execution_id: str
    type: RuntimeEventType
    message: str
    data: dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
