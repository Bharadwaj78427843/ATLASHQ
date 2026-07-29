"""
app/ai/interfaces/prompt.py

Vendor-neutral abstraction for prompt template providers (filesystem,
database, ...). Supports namespaces, versioning, and template variables.
"""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.ai.interfaces.base import BaseProvider


@dataclass
class PromptTemplate:
    name: str
    namespace: str
    version: str
    template: str
    variables: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def render(self, **kwargs: Any) -> str:
        """Render the template, substituting `{variable}` placeholders."""
        missing = [v for v in self.variables if v not in kwargs]
        if missing:
            raise KeyError(f"Missing template variables: {missing}")
        return self.template.format(**kwargs)


class PromptProvider(BaseProvider):
    """Contract for providers that load and resolve prompt templates."""

    @abstractmethod
    async def get_prompt(
        self, name: str, *, namespace: str = "default", version: str | None = None
    ) -> PromptTemplate:
        """Resolve a prompt template by name/namespace/version.

        `version=None` resolves to the latest available version.
        """
        raise NotImplementedError

    @abstractmethod
    async def list_prompts(self, namespace: str = "default") -> list[str]:
        """List prompt names available within a namespace."""
        raise NotImplementedError
