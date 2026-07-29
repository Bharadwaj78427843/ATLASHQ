from __future__ import annotations

from abc import ABC, abstractmethod

from app.ai.interfaces.base import HealthCheckResult
from app.ai.knowledge.models import (
    KnowledgeDeleteRequest,
    KnowledgeIngestRequest,
    KnowledgeIngestResult,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
    KnowledgeStatus,
    KnowledgeSyncRequest,
    KnowledgeSyncResult,
)


class KnowledgeProvider(ABC):
    provider_name: str = "knowledge-base"

    @abstractmethod
    async def health(self) -> HealthCheckResult:
        raise NotImplementedError

    @abstractmethod
    async def ingest(self, request: KnowledgeIngestRequest) -> KnowledgeIngestResult:
        raise NotImplementedError

    @abstractmethod
    async def search(self, request: KnowledgeSearchRequest) -> KnowledgeSearchResult:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, request: KnowledgeDeleteRequest) -> None:
        raise NotImplementedError

    @abstractmethod
    async def sync(self, request: KnowledgeSyncRequest) -> KnowledgeSyncResult:
        raise NotImplementedError

    @abstractmethod
    async def status(self) -> KnowledgeStatus:
        raise NotImplementedError
