"""
app/ai/config/models.py

Pydantic schema for the AI platform configuration block. This is the
single source of truth for "which provider is active for which category"
and the options passed to it — nothing else should hardcode provider
selection.
"""
from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class ProviderSelection(BaseModel):
    """Which provider is active for one category, and its options."""

    provider: str
    options: dict[str, Any] = Field(default_factory=dict)


class RuntimeSettings(BaseModel):
    default_agent: str = "execution"
    enable_streaming: bool = True
    enable_memory: bool = True
    enable_planner: bool = True
    max_parallel_tasks: int = 4
    max_tool_retries: int = 2
    default_timeout: int = 120


class AIConfig(BaseModel):
    """Top-level `ai:` configuration block."""

    knowledge: ProviderSelection = Field(default_factory=lambda: ProviderSelection(provider="native"))
    runtime: RuntimeSettings = Field(default_factory=RuntimeSettings)
    llm: ProviderSelection = Field(default_factory=lambda: ProviderSelection(provider="mock"))
    retrieval: ProviderSelection = Field(default_factory=lambda: ProviderSelection(provider="mock"))
    embeddings: ProviderSelection = Field(default_factory=lambda: ProviderSelection(provider="mock"))
    vectorstore: ProviderSelection = Field(default_factory=lambda: ProviderSelection(provider="mock"))
    documents: ProviderSelection = Field(default_factory=lambda: ProviderSelection(provider="mock"))
    memory: ProviderSelection = Field(default_factory=lambda: ProviderSelection(provider="mock"))
    prompts: ProviderSelection = Field(default_factory=lambda: ProviderSelection(provider="filesystem"))
    agents: ProviderSelection = Field(default_factory=lambda: ProviderSelection(provider="mock"))

    def selection_for(self, category: str) -> ProviderSelection:
        """Return the `ProviderSelection` for a category name (e.g. "llm")."""
        try:
            return getattr(self, category)
        except AttributeError as exc:
            raise KeyError(f"Unknown AI config category: {category}") from exc
