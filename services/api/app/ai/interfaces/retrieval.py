"""
app/ai/interfaces/retrieval.py

Vendor-neutral abstraction for retrieval providers (RAGFlow, LangChain,
LlamaIndex, Azure AI Search, Elastic, OpenSearch, ...).
"""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.ai.interfaces.base import BaseProvider


@dataclass
class RetrievalQuery:
    text: str
    workspace_id: str | None = None
    project_id: str | None = None
    top_k: int = 5
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievedChunk:
    id: str
    content: str
    score: float
    source_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class RetrievalResult:
    chunks: list[RetrievedChunk] = field(default_factory=list)
    raw: dict[str, Any] = field(default_factory=dict)


class RetrievalProvider(BaseProvider):
    """Contract for providers that turn a query into ranked context chunks."""

    @abstractmethod
    async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
        """Return the top-ranked chunks relevant to `query`."""
        raise NotImplementedError
