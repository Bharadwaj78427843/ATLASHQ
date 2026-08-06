from __future__ import annotations

from datetime import datetime, timezone

from app.ai.runtime.context import ExecutionContext
from app.ai.runtime.memory import RuntimeMemoryStore
from app.ai.skills_runtime.model_adapter import ModelAdapter
from app.ai.skills_runtime.models import SkillExecutionRequest, SkillPackage, SkillStepTrace
from app.ai.skills_runtime.permissions import ToolPermissionEngine
from app.ai.telemetry.hooks import TelemetryContext


class WorkflowExecutor:
    def __init__(
        self,
        model_adapter: ModelAdapter,
        permission_engine: ToolPermissionEngine,
        memory_store: RuntimeMemoryStore,
        telemetry: TelemetryContext,
    ) -> None:
        self._model_adapter = model_adapter
        self._permission_engine = permission_engine
        self._memory_store = memory_store
        self._telemetry = telemetry

    async def run(self, skill: SkillPackage, execution_id: str, request: SkillExecutionRequest) -> tuple[list[SkillStepTrace], dict]:
        traces: list[SkillStepTrace] = []
        step_outputs: dict[str, str] = {}

        context = ExecutionContext(
            execution_id=execution_id,
            workspace_id=request.workspace_id,
            organization_id=request.organization_id,
            project_id=request.project_id,
            repository_id=request.repository_id,
            session_id=request.session_id,
            user_id=request.user_id,
            prompt=request.prompt,
            metadata=request.metadata,
            request_metadata=request.request_metadata,
            permissions=request.permissions,
            memory=request.memory,
            model=request.model,
            trace=request.trace,
            configuration=request.configuration,
            environment=request.environment,
            correlation_id=request.correlation_id,
            deadline=request.deadline,
            cancelled=request.cancelled,
        )

        for step in skill.workflow:
            trace = SkillStepTrace(step_id=step.id, status="running", message=step.description)
            traces.append(trace)

            tools_for_step = request.step_tools.get(step.id, [])
            self._permission_engine.ensure_step_tools_allowed(skill, step.id, tools_for_step)

            with self._telemetry.timed(
                "ai.skills_runtime.step",
                tags={"skill": skill.name, "step": step.id},
            ):
                output = await self._model_adapter.run_step(skill=skill, step=step, prompt=request.prompt, metadata=request.metadata)

            step_outputs[step.id] = output
            trace.status = "completed"
            trace.output = output
            trace.finished_at = datetime.now(timezone.utc)

            await self._memory_store.append(
                context,
                "skill_steps",
                {
                    "skill": skill.name,
                    "step": step.id,
                    "output": output,
                },
            )

        outputs = self._build_declared_outputs(skill, step_outputs)
        await self._memory_store.append(
            context,
            "skill_results",
            {
                "skill": skill.name,
                "outputs": outputs,
            },
        )
        return traces, outputs

    def _build_declared_outputs(self, skill: SkillPackage, step_outputs: dict[str, str]) -> dict:
        def by_step(step_id: str) -> str:
            return step_outputs.get(step_id, "")

        fallback = "\n\n".join([f"{k}: {v}" for k, v in step_outputs.items()])
        outputs: dict[str, str] = {}

        for name in skill.interfaces.outputs:
            lowered = name.lower()
            if "status" in lowered:
                outputs[name] = by_step("sprint_discovery") or fallback
            elif "plan" in lowered:
                outputs[name] = by_step("prioritize") or by_step("delegate") or fallback
            elif "release" in lowered:
                outputs[name] = by_step("release_gate") or by_step("manager_review") or fallback
            else:
                outputs[name] = fallback

        return outputs