from __future__ import annotations

from typing import Any

import httpx

from app.ai.interfaces.base import HealthCheckResult, HealthStatus
from app.ai.knowledge.base import KnowledgeProvider
from app.ai.knowledge.exceptions import KnowledgeProviderError
from app.ai.knowledge.models import (
    KnowledgeDeleteRequest,
    KnowledgeIngestRequest,
    KnowledgeIngestResult,
    KnowledgeSearchRequest,
    KnowledgeSearchResult,
    KnowledgeSearchResultChunk,
    KnowledgeStatus,
    KnowledgeSyncRequest,
    KnowledgeSyncResult,
)
from app.ai.telemetry.hooks import TelemetryContext, get_telemetry


class RAGFlowKnowledgeProvider(KnowledgeProvider):
    provider_name = "ragflow"

    def __init__(self, config: dict[str, Any] | None = None, telemetry: TelemetryContext | None = None) -> None:
        self._config = config or {}
        self._telemetry = telemetry or get_telemetry()
        self._base_url = self._config.get("base_url", "").rstrip("/")
        self._api_key = self._config.get("api_key", "")
        self._timeout = float(self._config.get("timeout_seconds", 30))
        self._endpoints = self._config.get("endpoints", {})

    def _endpoint(self, key: str) -> str:
        path = self._endpoints.get(key)
        if not path:
            raise KnowledgeProviderError(
                f"Missing RAGFlow endpoint config for '{key}'.",
                provider=self.provider_name,
                category="knowledge",
            )
        return f"{self._base_url}/{path.lstrip('/')}"

    def _headers(self) -> dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self._api_key:
            headers["Authorization"] = f"Bearer {self._api_key}"
        return headers

    async def _request(self, method: str, endpoint_key: str, *, json: dict[str, Any] | None = None) -> dict[str, Any]:
        if not self._base_url:
            raise KnowledgeProviderError(
                "RAGFlow base_url is not configured.",
                provider=self.provider_name,
                category="knowledge",
            )
        url = self._endpoint(endpoint_key)
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            response = await client.request(method, url, headers=self._headers(), json=json)
            try:
                response.raise_for_status()
            except httpx.HTTPError as exc:
                raise KnowledgeProviderError(
                    f"RAGFlow request failed for {endpoint_key}: {exc}",
                    provider=self.provider_name,
                    category="knowledge",
                    details={"status_code": response.status_code, "body": response.text},
                ) from exc
            if not response.text:
                return {}
            data = response.json()
            if isinstance(data, dict):
                return data
            return {"data": data}

    async def health(self) -> HealthCheckResult:
        try:
            await self._request("GET", "health")
            return HealthCheckResult(status=HealthStatus.HEALTHY, message="RAGFlow health endpoint reachable.")
        except Exception as exc:  # noqa: BLE001
            return HealthCheckResult(status=HealthStatus.UNHEALTHY, message=str(exc))

    async def ingest(self, request: KnowledgeIngestRequest) -> KnowledgeIngestResult:
        with self._telemetry.timed("ai.knowledge.ragflow.ingest"):
            payload = {
                "document_id": request.document_ref.id,
                "name": request.document_ref.name,
                "uri": request.document_ref.uri,
                "collection": request.collection,
                "workspace_id": request.workspace_id,
                "metadata": request.metadata,
            }
            result = await self._request("POST", "upload_document", json=payload)
            return KnowledgeIngestResult(
                document_id=request.document_ref.id,
                chunks_indexed=int(result.get("chunks_indexed", 0)),
                collection=request.collection,
                provider=self.provider_name,
            )

    async def search(self, request: KnowledgeSearchRequest) -> KnowledgeSearchResult:
        with self._telemetry.timed("ai.knowledge.ragflow.search"):
            payload = {
                "query": request.query,
                "workspace_id": request.workspace_id,
                "top_k": request.top_k,
                "collection": request.collection,
                "filters": request.filters,
                "mode": "hybrid",
            }
            result = await self._request("POST", "search", json=payload)
            chunks = [
                KnowledgeSearchResultChunk(
                    id=str(item.get("id", "")),
                    content=str(item.get("content", "")),
                    score=float(item.get("score", 0.0)),
                    metadata=item.get("metadata", {}),
                )
                for item in result.get("results", [])
            ]
            return KnowledgeSearchResult(
                answer=str(result.get("answer", "")),
                context_chunks=chunks,
                model=str(result.get("model", "")),
                provider=self.provider_name,
            )

    async def delete(self, request: KnowledgeDeleteRequest) -> None:
        await self._request(
            "POST",
            "delete_dataset",
            json={"source_id": request.source_id, "collection": request.collection},
        )

    async def sync(self, request: KnowledgeSyncRequest) -> KnowledgeSyncResult:
        with self._telemetry.timed("ai.knowledge.ragflow.sync"):
            payload = {
                "workspace_id": request.workspace_id,
                "source_type": request.source_type,
                "source_uri": request.source_uri,
                "branch": request.branch,
                "metadata": request.metadata,
            }
            result = await self._request("POST", "upload_repository", json=payload)
            return KnowledgeSyncResult(status=str(result.get("status", "queued")), provider=self.provider_name, details=result)

    async def status(self) -> KnowledgeStatus:
        result = await self._request("GET", "status")
        return KnowledgeStatus(
            provider=self.provider_name,
            status=str(result.get("status", "unknown")),
            details=result,
        )
