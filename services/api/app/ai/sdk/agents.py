from __future__ import annotations

from dataclasses import asdict

from app.ai.runtime.models import AgentExecutionRequest


class AgentPipeline:
    def __init__(self, runtime) -> None:
        self._runtime = runtime

    async def execute(self, prompt: str, workspace_id: str | None = None, organization_id: str | None = None, user_id: str | None = None) -> dict:
        result = await self._runtime.execute(
            AgentExecutionRequest(
                prompt=prompt,
                workspace_id=workspace_id,
                organization_id=organization_id,
                user_id=user_id,
            )
        )
        return asdict(result)

    async def plan(self, prompt: str, workspace_id: str | None = None, organization_id: str | None = None, user_id: str | None = None) -> dict:
        execution_id, plan = await self._runtime.plan(
            AgentExecutionRequest(
                prompt=prompt,
                workspace_id=workspace_id,
                organization_id=organization_id,
                user_id=user_id,
            )
        )
        return {
            "execution_id": execution_id,
            "goal": plan.goal,
            "steps": [asdict(step) for step in plan.steps],
            "metadata": plan.metadata,
        }

    async def status(self, execution_id: str) -> dict:
        return self._runtime.status(execution_id)

    async def cancel(self, execution_id: str) -> dict:
        return self._runtime.cancel(execution_id)

    async def resume(self, execution_id: str) -> dict:
        # Resume semantics can be upgraded later with persisted queues.
        return {"execution_id": execution_id, "status": "resume_not_implemented"}

    async def events(self, execution_id: str) -> dict:
        return {"execution_id": execution_id, "events": self._runtime.events(execution_id)}
