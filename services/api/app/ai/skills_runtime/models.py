from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any


class SkillExecutionStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    BLOCKED = "blocked"


@dataclass(frozen=True)
class WorkflowStep:
    id: str
    description: str
    parallelizable: bool = False
    produces: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class PolicyRule:
    id: str
    description: str
    severity: str


@dataclass(frozen=True)
class ToolPermissions:
    can_edit_code: bool = True
    can_run_tests: bool = True
    can_release: bool = False
    can_modify_policies: bool = False


@dataclass(frozen=True)
class SkillArtifacts:
    prompt: str
    workflow: str
    policies: str
    tools: str


@dataclass(frozen=True)
class SkillInterfaces:
    inputs: list[str] = field(default_factory=list)
    outputs: list[str] = field(default_factory=list)
    requires: list[str] = field(default_factory=list)
    produces: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SkillPackage:
    id: str
    name: str
    display_name: str
    version: str
    description: str
    owners: list[str]
    prompt: str
    workflow: list[WorkflowStep]
    policies: list[PolicyRule]
    tools: list[str]
    permissions: ToolPermissions
    interfaces: SkillInterfaces
    contracts: dict[str, str] = field(default_factory=dict)
    input_schema: dict[str, Any] | None = None
    output_schema: dict[str, Any] | None = None
    tests: list[str] = field(default_factory=list)
    knowledge: list[str] = field(default_factory=list)
    handoffs: list[dict[str, Any]] = field(default_factory=list)
    success_criteria: list[str] = field(default_factory=list)


@dataclass
class SkillExecutionRequest:
    skill_id: str
    prompt: str
    workspace_id: str | None = None
    organization_id: str | None = None
    user_id: str | None = None
    project_id: str | None = None
    repository_id: str | None = None
    session_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)
    policy_context: dict[str, Any] = field(default_factory=dict)
    step_tools: dict[str, list[str]] = field(default_factory=dict)
    permissions: dict[str, Any] = field(default_factory=dict)
    memory: dict[str, Any] = field(default_factory=dict)
    model: dict[str, Any] = field(default_factory=dict)
    trace: dict[str, Any] = field(default_factory=dict)
    configuration: dict[str, Any] = field(default_factory=dict)
    environment: dict[str, Any] = field(default_factory=dict)
    correlation_id: str | None = None
    request_metadata: dict[str, Any] = field(default_factory=dict)
    deadline: datetime | None = None
    cancelled: bool = False


@dataclass
class SkillStepTrace:
    step_id: str
    status: str
    started_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    finished_at: datetime | None = None
    message: str = ""
    output: Any = None


@dataclass
class SkillExecutionResult:
    execution_id: str
    skill_id: str
    status: SkillExecutionStatus
    outputs: dict[str, Any] = field(default_factory=dict)
    traces: list[SkillStepTrace] = field(default_factory=list)
    policy_violations: list[str] = field(default_factory=list)
    dependency_warnings: list[str] = field(default_factory=list)
    error: str | None = None