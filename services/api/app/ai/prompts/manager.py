"""
app/ai/prompts/manager.py

`PromptManager` is a thin convenience wrapper over a resolved
`PromptProvider` for rendering templates. It never hardcodes prompt text —
all content is loaded through the active provider.
"""
from __future__ import annotations

from app.ai.interfaces.prompt import PromptProvider, PromptTemplate


class PromptManager:
    def __init__(self, provider: PromptProvider) -> None:
        self._provider = provider

    async def get(self, name: str, *, namespace: str = "default", version: str | None = None) -> PromptTemplate:
        return await self._provider.get_prompt(name, namespace=namespace, version=version)

    async def render(
        self, name: str, *, namespace: str = "default", version: str | None = None, **variables: object
    ) -> str:
        template = await self.get(name, namespace=namespace, version=version)
        return template.render(**variables)

    async def list(self, namespace: str = "default") -> list[str]:
        return await self._provider.list_prompts(namespace)
