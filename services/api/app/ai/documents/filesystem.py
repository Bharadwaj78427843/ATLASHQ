from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from app.ai.exceptions.errors import DocumentError
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.document import DocumentContent, DocumentProvider, DocumentQuery, DocumentRef


class FilesystemDocumentProvider(DocumentProvider):
    provider_name = "filesystem"

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)
        root = self._config.get("root")
        self._root = Path(root).resolve() if root else None

    def _resolve_path(self, uri: str) -> Path:
        parsed = urlparse(uri)
        if parsed.scheme == "file":
            candidate = Path(parsed.path)
        else:
            candidate = Path(uri)

        if not candidate.is_absolute() and self._root is not None:
            candidate = self._root / candidate

        resolved = candidate.resolve()
        if self._root is not None and self._root not in resolved.parents and resolved != self._root:
            raise DocumentError(
                f"Path '{resolved}' escapes configured root '{self._root}'.",
                provider=self.provider_name,
                category="documents",
            )
        return resolved

    async def list_documents(self, query: DocumentQuery) -> list[DocumentRef]:
        if self._root is None or not self._root.exists():
            return []
        refs: list[DocumentRef] = []
        for path in self._root.rglob("*"):
            if not path.is_file():
                continue
            refs.append(
                DocumentRef(
                    id=str(path),
                    name=path.name,
                    uri=str(path),
                    mime_type="application/octet-stream",
                )
            )
        return refs

    async def fetch(self, ref: DocumentRef) -> DocumentContent:
        path = self._resolve_path(ref.uri)
        if not path.exists() or not path.is_file():
            raise DocumentError(
                f"Document file does not exist: {path}",
                provider=self.provider_name,
                category="documents",
            )

        content = path.read_bytes()
        text: str | None
        if ref.mime_type == "application/pdf" or path.suffix.lower() == ".pdf":
            try:
                from pypdf import PdfReader
                reader = PdfReader(str(path))
                text = "\n".join((page.extract_text() or "") for page in reader.pages)
            except Exception as exc:  # noqa: BLE001
                raise DocumentError(
                    f"Failed to extract PDF text for '{path.name}': {exc}",
                    provider=self.provider_name,
                    category="documents",
                ) from exc
        else:
            text = content.decode("utf-8", errors="ignore")

        return DocumentContent(ref=ref, content=content, text=text)

    async def health(self) -> HealthCheckResult:
        if self._root is None:
            return HealthCheckResult(status=HealthStatus.HEALTHY, message="Filesystem provider enabled without root restriction.")
        if self._root.exists():
            return HealthCheckResult(status=HealthStatus.HEALTHY, message=f"Filesystem root available: {self._root}")
        return HealthCheckResult(status=HealthStatus.DEGRADED, message=f"Filesystem root missing: {self._root}")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(features=frozenset({"list", "fetch", "pdf-extract", "filesystem"}))
