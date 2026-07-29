"""
app/ai/interfaces/embedding.py

Vendor-neutral abstraction for embedding providers (OpenAI, Azure,
SentenceTransformers, VoyageAI, Ollama, ...).
"""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.ai.interfaces.base import BaseProvider


@dataclass
class EmbeddingRequest:
    inputs: list[str]
    model: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class EmbeddingResponse:
    vectors: list[list[float]]
    model: str
    dimensions: int
    raw: dict[str, Any] = field(default_factory=dict)


class EmbeddingProvider(BaseProvider):
    """Contract for providers that turn text into dense vectors."""

    @abstractmethod
    async def embed(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Embed a batch of text inputs."""
        raise NotImplementedError
