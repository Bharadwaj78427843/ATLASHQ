"""
app/ai/prompts/providers.py

Prompt template providers: filesystem-backed (implemented) and a
database-backed stub for a future implementation.
"""
from __future__ import annotations

import re
from pathlib import Path

from app.ai.exceptions.errors import PromptError
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.prompt import PromptProvider, PromptTemplate

_VAR_PATTERN = re.compile(r"\{(\w+)\}")
_DEFAULT_ROOT = Path(__file__).parent / "templates"


class FilesystemPromptProvider(PromptProvider):
    """Loads prompt templates from `{root}/{namespace}/{name}@{version}.txt`.

    Template variables are `{like_this}` placeholders, discovered
    automatically from the file content. When `version` is omitted, the
    lexicographically greatest version file for that name is used.
    """

    provider_name = "filesystem"

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)
        self._root = Path(self._config.get("root", _DEFAULT_ROOT))

    def _namespace_dir(self, namespace: str) -> Path:
        return self._root / namespace

    async def get_prompt(
        self, name: str, *, namespace: str = "default", version: str | None = None
    ) -> PromptTemplate:
        ns_dir = self._namespace_dir(namespace)
        candidates = sorted(ns_dir.glob(f"{name}@*.txt")) if ns_dir.exists() else []
        if not candidates:
            raise PromptError(
                f"Prompt '{name}' not found in namespace '{namespace}' under '{self._root}'.",
                provider=self.provider_name,
                category="prompts",
            )

        if version is not None:
            match = next((p for p in candidates if p.stem == f"{name}@{version}"), None)
            if match is None:
                raise PromptError(
                    f"Prompt '{name}' has no version '{version}' in namespace '{namespace}'.",
                    provider=self.provider_name,
                    category="prompts",
                )
        else:
            match = candidates[-1]

        resolved_version = match.stem.split("@", 1)[1]
        text = match.read_text(encoding="utf-8")
        variables = sorted(set(_VAR_PATTERN.findall(text)))
        return PromptTemplate(
            name=name,
            namespace=namespace,
            version=resolved_version,
            template=text,
            variables=variables,
        )

    async def list_prompts(self, namespace: str = "default") -> list[str]:
        ns_dir = self._namespace_dir(namespace)
        if not ns_dir.exists():
            return []
        return sorted({p.stem.split("@", 1)[0] for p in ns_dir.glob("*@*.txt")})

    async def health(self) -> HealthCheckResult:
        if self._root.exists():
            return HealthCheckResult(status=HealthStatus.HEALTHY, message=f"Prompt root '{self._root}' is readable.")
        return HealthCheckResult(status=HealthStatus.DEGRADED, message=f"Prompt root '{self._root}' does not exist.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"versioning", "namespaces", "filesystem"}))


class DatabasePromptProvider(PromptProvider):
    """Stub for a future database-backed prompt store (with an admin UI)."""

    provider_name = "database"

    async def get_prompt(
        self, name: str, *, namespace: str = "default", version: str | None = None
    ) -> PromptTemplate:
        raise PromptError(
            "'database' is a stub prompt provider. Implement get_prompt() to enable it.",
            provider=self.provider_name,
            category="prompts",
        )

    async def list_prompts(self, namespace: str = "default") -> list[str]:
        raise PromptError(
            "'database' is a stub prompt provider. Implement list_prompts() to enable it.",
            provider=self.provider_name,
            category="prompts",
        )

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(status=HealthStatus.UNKNOWN, message="'database' is a stub — not implemented.")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset(), metadata={"stub": True})

    def validate(self) -> list[str]:
        return ["'database' is a stub provider and cannot be used in production."]
