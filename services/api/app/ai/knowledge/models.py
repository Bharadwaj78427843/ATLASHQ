from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from app.ai.interfaces.document import DocumentRef


@dataclass
class KnowledgeIngestRequest:
    document_ref: DocumentRef
    collection: str = "default"
    workspace_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeIngestResult:
    document_id: str
    chunks_indexed: int
    collection: str
    provider: str


@dataclass
class KnowledgeSearchRequest:
    query: str
    workspace_id: str | None = None
    top_k: int = 5
    collection: str = "default"
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeSearchResultChunk:
    id: str
    content: str
    score: float
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeSearchResult:
    answer: str
    context_chunks: list[KnowledgeSearchResultChunk] = field(default_factory=list)
    model: str = ""
    provider: str = ""


@dataclass
class KnowledgeDeleteRequest:
    source_id: str
    collection: str = "default"


@dataclass
class KnowledgeSyncRequest:
    workspace_id: str
    source_type: str
    source_uri: str
    branch: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeSyncResult:
    status: str
    provider: str
    details: dict[str, Any] = field(default_factory=dict)


@dataclass
class KnowledgeStatus:
    provider: str
    status: str
    details: dict[str, Any] = field(default_factory=dict)
