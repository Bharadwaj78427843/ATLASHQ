"""
app/ai/registry/types.py

Types shared by the provider registry: the fixed set of provider
categories the platform recognizes, and the metadata recorded for each
registration.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable

from app.ai.interfaces.base import BaseProvider

#: A factory callable that builds a provider instance from a config dict.
ProviderFactoryFn = Callable[[dict[str, Any]], BaseProvider]


class ProviderCategory(str, Enum):
    """The fixed set of provider categories the AI platform supports.

    Adding a new *provider* never requires touching this enum. Adding a new
    *category* (rare) is the one platform-level change that does.
    """

    LLM = "llm"
    RETRIEVAL = "retrieval"
    EMBEDDING = "embeddings"
    VECTORSTORE = "vectorstore"
    DOCUMENT = "documents"
    MEMORY = "memory"
    PROMPT = "prompts"
    AGENT = "agents"


@dataclass
class ProviderRegistration:
    """A registered-but-not-necessarily-instantiated provider.

    Exactly one of `factory` or `module_path` must be supplied. `module_path`
    enables lazy loading: the module is only imported the first time the
    provider is resolved, so registering every stub provider up front never
    pays the import cost of unused vendor SDKs.
    """

    category: ProviderCategory
    name: str
    factory: ProviderFactoryFn | None = None
    module_path: str | None = None  # "app.ai.llm.mock:MockLLMProvider"
    #: Other providers this one depends on, as "category:name" keys
    #: (matching `dependency_graph()`'s keys), e.g. ("memory:redis",).
    depends_on: tuple[str, ...] = ()
    description: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)

    def key(self) -> tuple[ProviderCategory, str]:
        return (self.category, self.name)
