"""
app/ai/documents/stubs.py

Lightweight stubs for future document source providers. Each satisfies the
`DocumentProvider` contract but raises `DocumentError` if invoked.
"""
from __future__ import annotations

from app.ai.exceptions.errors import DocumentError
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.document import DocumentContent, DocumentProvider, DocumentQuery, DocumentRef


class _StubDocumentProvider(DocumentProvider):
    def _not_implemented(self) -> DocumentError:
        return DocumentError(
            f"'{self.provider_name}' is a stub provider. Implement its methods to enable it.",
            provider=self.provider_name,
            category="documents",
        )

    async def list_documents(self, query: DocumentQuery) -> list[DocumentRef]:
        raise self._not_implemented()

    async def fetch(self, ref: DocumentRef) -> DocumentContent:
        raise self._not_implemented()

    async def health(self) -> HealthCheckResult:
        return HealthCheckResult(
            status=HealthStatus.UNKNOWN,
            message=f"'{self.provider_name}' is a stub — not implemented.",
        )

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset(), metadata={"stub": True})

    def validate(self) -> list[str]:
        return [f"'{self.provider_name}' is a stub provider and cannot be used in production."]


class FilesystemDocumentProvider(_StubDocumentProvider):
    provider_name = "filesystem"


class GitHubDocumentProvider(_StubDocumentProvider):
    provider_name = "github"


class GitLabDocumentProvider(_StubDocumentProvider):
    provider_name = "gitlab"


class AzureDevOpsDocumentProvider(_StubDocumentProvider):
    provider_name = "azure-devops"


class SharePointDocumentProvider(_StubDocumentProvider):
    provider_name = "sharepoint"


class ConfluenceDocumentProvider(_StubDocumentProvider):
    provider_name = "confluence"


class S3DocumentProvider(_StubDocumentProvider):
    provider_name = "s3"


class GoogleDriveDocumentProvider(_StubDocumentProvider):
    provider_name = "google-drive"


class OneDriveDocumentProvider(_StubDocumentProvider):
    provider_name = "onedrive"
