from __future__ import annotations

from app.ai.factory.factory import ProviderFactory
from app.ai.interfaces.llm import LLMMessage, LLMRequest
from app.ai.skills_runtime.models import SkillPackage, WorkflowStep


class ModelAdapter:
    def __init__(self, factory: ProviderFactory) -> None:
        self._factory = factory

    async def run_step(self, skill: SkillPackage, step: WorkflowStep, prompt: str, metadata: dict | None = None) -> str:
        llm = await self._factory.create_llm()
        request = LLMRequest(
            messages=[
                LLMMessage(role="system", content=skill.prompt),
                LLMMessage(
                    role="user",
                    content=(
                        f"Skill: {skill.display_name}\n"
                        f"Step: {step.id}\n"
                        f"Step Description: {step.description}\n"
                        f"User Prompt: {prompt}\n"
                        "Return concise, structured execution notes for this step."
                    ),
                ),
            ],
            metadata=metadata or {},
        )
        response = await llm.generate(request)
        return response.content
