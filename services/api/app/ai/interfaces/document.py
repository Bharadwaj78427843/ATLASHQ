"""
app/ai/interfaces/document.py

Vendor-neutral abstraction for document source providers (Filesystem,
GitHub, GitLab, Azure DevOps, SharePoint, Confluence, S3, Google Drive,
OneDrive, ...).
"""
from __future__ import annotations

from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any

from app.ai.interfaces.base import BaseProvider


@dataclass
class DocumentQuery:
    workspace_id: str | None = None
    path_prefix: str | None = None
    filters: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentRef:
    id: str
    name: str
    uri: str
    mime_type: str = "application/octet-stream"
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class DocumentContent:
    ref: DocumentRef
    content: bytes
    text: str | None = None


class DocumentProvider(BaseProvider):
    """Contract for providers that list and fetch source documents."""

    @abstractmethod
    async def list_documents(self, query: DocumentQuery) -> list[DocumentRef]:
        """List documents visible to `query` without fetching their content."""
        raise NotImplementedError

    @abstractmethod
    async def fetch(self, ref: DocumentRef) -> DocumentContent:
        """Fetch the raw content of a single document reference."""
        raise NotImplementedError
