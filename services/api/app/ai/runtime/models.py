from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class ExecutionStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING = "waiting"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class StepStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class PlanStep:
    id: str
    task: str
    priority: int = 3
    dependencies: list[str] = field(default_factory=list)
    expected_output: str = ""
    estimated_cost: float = 0.0
    tools: list[str] = field(default_factory=list)
    parallelizable: bool = False


@dataclass
class ExecutionPlan:
    goal: str
    steps: list[PlanStep]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class AgentExecutionRequest:
    prompt: str
    workspace_id: str | None = None
    organization_id: str | None = None
    user_id: str | None = None
    max_steps: int = 12
    timeout_seconds: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class StepResult:
    step_id: str
    status: StepStatus
    output: Any = None
    evidence: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    duration_ms: int = 0


@dataclass
class AgentExecutionResult:
    execution_id: str
    status: ExecutionStatus
    answer: str = ""
    steps: list[StepResult] = field(default_factory=list)
    evidence: list[dict[str, Any]] = field(default_factory=list)
    error: str | None = None
    started_at: datetime | None = None
    finished_at: datetime | None = None


@dataclass
class RuntimeConfig:
    default_agent: str = "execution"
    enable_streaming: bool = True
    enable_memory: bool = True
    enable_planner: bool = True
    max_parallel_tasks: int = 4
    max_tool_retries: int = 2
    default_timeout: int = 120
