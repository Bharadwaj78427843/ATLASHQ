"""
app/ai/interfaces/vectorstore.py

Vendor-neutral abstraction for vector store providers (pgvector, Qdrant,
Weaviate, Pinecone, Milvus, Redis Vector, ...).
"""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.ai.interfaces.base import BaseProvider


@dataclass
class VectorRecord:
    id: str
    vector: list[float]
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorQuery:
    vector: list[float]
    top_k: int = 5
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass
class VectorMatch:
    id: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


class VectorStoreProvider(BaseProvider):
    """Contract for providers that persist and query vector embeddings."""

    @abstractmethod
    async def upsert(self, collection: str, records: list[VectorRecord]) -> None:
        """Insert or update vector records in a collection/namespace."""
        raise NotImplementedError

    @abstractmethod
    async def query(self, collection: str, query: VectorQuery) -> list[VectorMatch]:
        """Return the nearest vectors to `query` within a collection."""
        raise NotImplementedError

    @abstractmethod
    async def delete(self, collection: str, ids: list[str]) -> None:
        """Remove vector records by id from a collection."""
        raise NotImplementedError
