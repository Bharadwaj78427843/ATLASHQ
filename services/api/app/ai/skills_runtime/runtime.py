from __future__ import annotations

import uuid

from app.ai.skills_runtime.dependency import DependencyResolver
from app.ai.skills_runtime.errors import PolicyBlockedError
from app.ai.skills_runtime.loader import SkillLoader
from app.ai.skills_runtime.models import SkillExecutionRequest, SkillExecutionResult, SkillExecutionStatus
from app.ai.skills_runtime.output_validator import OutputValidator
from app.ai.skills_runtime.policy import PolicyEngine
from app.ai.skills_runtime.registry import SkillRegistryService
from app.ai.skills_runtime.workflow_executor import WorkflowExecutor
from app.ai.telemetry.hooks import TelemetryContext


class SkillRuntime:
    def __init__(
        self,
        *,
        registry: SkillRegistryService,
        loader: SkillLoader,
        dependency_resolver: DependencyResolver,
        policy_engine: PolicyEngine,
        workflow_executor: WorkflowExecutor,
        output_validator: OutputValidator,
        telemetry: TelemetryContext,
    ) -> None:
        self.registry = registry
        self.loader = loader
        self.dependency_resolver = dependency_resolver
        self.policy_engine = policy_engine
        self.workflow_executor = workflow_executor
        self.output_validator = output_validator
        self.telemetry = telemetry

    async def execute(self, request: SkillExecutionRequest) -> SkillExecutionResult:
        execution_id = str(uuid.uuid4())
        skill = self.loader.load(request.skill_id)

        known = self.registry.known_skill_ids()
        dependency_warnings = self.dependency_resolver.resolve(skill, known)

        policy_violations = self.policy_engine.evaluate(skill.policies, request.policy_context)
        if policy_violations:
            return SkillExecutionResult(
                execution_id=execution_id,
                skill_id=request.skill_id,
                status=SkillExecutionStatus.BLOCKED,
                policy_violations=policy_violations,
                dependency_warnings=dependency_warnings,
                error=str(PolicyBlockedError("Blocked by policy engine")),
            )

        try:
            with self.telemetry.timed("ai.skills_runtime.execute", tags={"skill": skill.name}):
                traces, outputs = await self.workflow_executor.run(skill, execution_id, request)
                if skill.output_schema:
                    self.output_validator.validate_schema(skill.output_schema, outputs)
                else:
                    self.output_validator.validate(skill.interfaces.outputs, outputs)
                return SkillExecutionResult(
                    execution_id=execution_id,
                    skill_id=request.skill_id,
                    status=SkillExecutionStatus.COMPLETED,
                    outputs=outputs,
                    traces=traces,
                    policy_violations=policy_violations,
                    dependency_warnings=dependency_warnings,
                )
        except Exception as exc:  # noqa: BLE001
            return SkillExecutionResult(
                execution_id=execution_id,
                skill_id=request.skill_id,
                status=SkillExecutionStatus.FAILED,
                error=str(exc),
                policy_violations=policy_violations,
                dependency_warnings=dependency_warnings,
            )