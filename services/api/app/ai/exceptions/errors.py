"""
app/ai/exceptions/errors.py

Exception hierarchy for the AI Platform. Every error raised by a provider,
the registry, the factory, or the orchestrator must be (or wrap) one of
these types so callers can handle failures generically without knowing
which vendor is behind the active provider.
"""
from __future__ import annotations

from typing import Any


class AIError(Exception):
    """Base class for all AI platform errors."""

    def __init__(
        self,
        message: str,
        *,
        provider: str | None = None,
        category: str | None = None,
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.provider = provider
        self.category = category
        self.details = details or {}

    def __str__(self) -> str:  # pragma: no cover - trivial
        prefix = f"[{self.category}:{self.provider}] " if self.provider else ""
        return f"{prefix}{self.message}"


class ProviderError(AIError):
    """A provider failed to perform a requested operation."""


class ProviderNotFoundError(ProviderError):
    """No provider is registered under the requested category/name."""


class ProviderNotRegisteredError(ProviderError):
    """A provider was resolved before being registered with the registry."""


class ConfigurationError(AIError):
    """AI platform configuration is missing, malformed, or invalid."""


class RetrievalError(ProviderError):
    """A retrieval provider failed to return results."""


class EmbeddingError(ProviderError):
    """An embedding provider failed to embed input."""


class VectorStoreError(ProviderError):
    """A vector store provider failed to read or write vectors."""


class DocumentError(ProviderError):
    """A document provider failed to list or fetch content."""


class MemoryProviderError(ProviderError):
    """A memory provider failed to read or write state."""


class PromptError(AIError):
    """A prompt could not be loaded, rendered, or resolved."""


class AgentError(AIError):
    """An agent failed to plan, execute, or coordinate a task."""


class LLMError(ProviderError):
    """An LLM provider failed to generate a completion."""
