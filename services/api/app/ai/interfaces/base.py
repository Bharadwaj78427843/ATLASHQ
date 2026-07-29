"""
app/ai/interfaces/base.py

The lifecycle contract every AI provider must implement, regardless of
category (LLM, retrieval, embeddings, vector store, documents, memory,
prompts, agents). The registry and factory only ever talk to providers
through this contract.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class HealthStatus(str, Enum):
    """Coarse-grained health signal reported by a provider."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    UNKNOWN = "unknown"


@dataclass
class HealthCheckResult:
    """Result of a provider health check. Never raises."""

    status: HealthStatus
    message: str = ""
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderCapabilities:
    """Declares what a specific provider instance supports at runtime.

    Business logic (and the orchestrator) can branch on capabilities
    instead of on provider identity, e.g. `if caps.supports("streaming")`
    rather than `if provider_name == "openai"`.
    """

    features: frozenset[str] = field(default_factory=frozenset)
    metadata: dict[str, Any] = field(default_factory=dict)

    def supports(self, feature: str) -> bool:
        return feature in self.features


class BaseProvider(ABC):
    """Abstract base every AI provider implementation must extend.

    Lifecycle:
        1. Instantiated by a factory with a plain config dict.
        2. `initialize()` is awaited once by the registry before first use.
        3. `health()` / `capabilities()` / `validate()` may be called any time.
        4. `shutdown()` is awaited once when the registry is torn down.
    """

    #: Machine name used for registration/config lookups, e.g. "azure-openai".
    provider_name: str = "base"

    def __init__(self, config: dict[str, Any] | None = None) -> None:
        self._config = dict(config or {})
        self._initialized = False

    async def initialize(self) -> None:
        """Acquire resources (clients, connections, sessions). Idempotent."""
        self._initialized = True

    async def shutdown(self) -> None:
        """Release resources acquired in `initialize()`. Idempotent."""
        self._initialized = False

    @abstractmethod
    async def health(self) -> HealthCheckResult:
        """Report current provider health. Must never raise."""
        raise NotImplementedError

    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        """Describe what this provider instance supports."""
        raise NotImplementedError

    def validate(self) -> list[str]:
        """Validate the active configuration.

        Returns a list of human-readable problems; an empty list means the
        configuration is valid. Default implementation assumes no required
        configuration.
        """
        return []

    def configuration(self) -> dict[str, Any]:
        """Return a shallow, redacted view of the active configuration."""
        return {k: v for k, v in self._config.items() if "secret" not in k.lower() and "key" not in k.lower()}

    @property
    def is_initialized(self) -> bool:
        return self._initialized
