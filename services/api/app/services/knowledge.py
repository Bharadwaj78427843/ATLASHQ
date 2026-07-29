import asyncio
import os
import shutil
import uuid
from datetime import datetime
from uuid import UUID

from fastapi import UploadFile

from app.ai.interfaces.document import DocumentRef
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.models.knowledge import IndexJob, KnowledgeDocument, KnowledgeSource
from app.repositories.knowledge import KnowledgeRepository
from app.schemas.knowledge import SearchResponse, SearchResultSnippet

class StorageService:
    def __init__(self, base_dir: str = "/tmp/atlas_knowledge"):
        self.base_dir = base_dir
        os.makedirs(self.base_dir, exist_ok=True)

    def save_file(self, file: UploadFile, source_id: UUID) -> str:
        source_dir = os.path.join(self.base_dir, str(source_id))
        os.makedirs(source_dir, exist_ok=True)
        file_path = os.path.join(source_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return file_path


class IndexingService:
    def __init__(self, repository: KnowledgeRepository, orchestrator: KnowledgeOrchestrator):
        self.repository = repository
        self.orchestrator = orchestrator

    async def index_source(self, source_id: UUID):
        """Indexes a source by delegating ingest to the configured knowledge provider."""
        job = self.repository.create_index_job(
            IndexJob(source_id=source_id, status="running", started_at=datetime.utcnow())
        )
        self.repository.update_source_status(source_id, "indexing")

        try:
            source = self.repository.get_source(source_id)
            if not source:
                self.repository.update_index_job(job.id, "failed", progress=0.0)
                return

            document_name = source.name
            document_ref = DocumentRef(
                id=str(source_id),
                name=document_name,
                uri=source.storage_path or f"source://{source_id}",
                mime_type="application/octet-stream",
                metadata={"workspace_id": str(source.workspace_id), "project_id": str(source.project_id) if source.project_id else None},
            )
            await self.orchestrator.ingest(document_ref, collection=str(source.workspace_id))

            self.repository.update_index_job(job.id, "completed", progress=1.0)
            self.repository.update_source_status(source_id, "ready")
        except Exception as exc:  # noqa: BLE001
            self.repository.update_index_job(job.id, "failed", progress=0.0)
            self.repository.update_source_status(source_id, "failed")
            failed = self.repository.db.query(IndexJob).filter(IndexJob.id == job.id).first()
            if failed:
                failed.error_message = str(exc)
                self.repository.db.commit()


class UploadService:
    def __init__(self, repository: KnowledgeRepository, storage_service: StorageService, indexing_service: IndexingService):
        self.repository = repository
        self.storage_service = storage_service
        self.indexing_service = indexing_service

    async def process_upload(self, file: UploadFile, workspace_id: UUID, user_id: UUID, project_id: UUID = None) -> KnowledgeSource:
        # Create Source record
        source = KnowledgeSource(
            workspace_id=workspace_id,
            project_id=project_id,
            name=file.filename,
            source_type="document",
            uploaded_by=user_id,
            size_bytes=file.size
        )
        source = self.repository.create_source(source)

        # Save to storage
        storage_path = self.storage_service.save_file(file, source.id)
        source.storage_path = storage_path
        self.repository.db.commit()

        # Create Document record
        doc = KnowledgeDocument(
            source_id=source.id,
            filename=file.filename,
            mime_type=file.content_type or "application/octet-stream"
        )
        self.repository.create_document(doc)

        # Kick off background indexing through the configured knowledge provider
        asyncio.create_task(self.indexing_service.index_source(source.id))

        return source


class SearchService:
    def __init__(self, repository: KnowledgeRepository, orchestrator: KnowledgeOrchestrator):
        self.repository = repository
        self.orchestrator = orchestrator

    async def search(self, query: str, workspace_id: UUID, limit: int = 10) -> SearchResponse:
        result = await self.orchestrator.search(query, workspace_id=str(workspace_id), top_k=limit)

        snippets: list[SearchResultSnippet] = []
        for chunk in result.context_chunks:
            source_id = chunk.metadata.get("source_id")
            source_name = chunk.metadata.get("source_name")
            try:
                source_uuid = UUID(str(source_id)) if source_id else uuid.uuid5(uuid.NAMESPACE_URL, chunk.id)
            except Exception:  # noqa: BLE001
                source_uuid = uuid.uuid5(uuid.NAMESPACE_URL, chunk.id)
            try:
                doc_uuid = UUID(str(chunk.id))
            except Exception:  # noqa: BLE001
                doc_uuid = uuid.uuid5(uuid.NAMESPACE_DNS, chunk.id)

            snippets.append(
                SearchResultSnippet(
                    source_id=source_uuid,
                    source_name=str(source_name or "Knowledge Source"),
                    document_id=doc_uuid,
                    filename=str(chunk.metadata.get("filename", "unknown")),
                    content=chunk.content,
                    score=chunk.score,
                )
            )

        return SearchResponse(query=query, results=snippets)


class ProviderConnector:
    """Base interface for repository providers"""
    def validate_repository(self, repository: str) -> bool:
        raise NotImplementedError
    
    def get_default_branch(self, repository: str) -> str:
        raise NotImplementedError


class GitHubConnector(ProviderConnector):
    def validate_repository(self, repository: str) -> bool:
        # Mock validation: ensure format is "owner/repo"
        parts = repository.split("/")
        return len(parts) == 2 and all(parts)

    def get_default_branch(self, repository: str) -> str:
        # Mock API call
        return "main"


class RepositoryService:
    def __init__(self, repository: KnowledgeRepository, indexing_service: IndexingService, orchestrator: KnowledgeOrchestrator):
        self.repository = repository
        self.indexing_service = indexing_service
        self.orchestrator = orchestrator
        self.connectors = {
            "github": GitHubConnector()
        }

    async def connect_repository(
        self, workspace_id: UUID, user_id: UUID, provider: str, repository_name: str, branch: str, project_id: UUID = None
    ) -> KnowledgeSource:
        connector = self.connectors.get(provider.lower())
        if not connector:
            raise ValueError(f"Unsupported provider: {provider}")

        if not connector.validate_repository(repository_name):
            raise ValueError(f"Invalid repository format for {provider}")

        # Create Source record
        source = KnowledgeSource(
            workspace_id=workspace_id,
            project_id=project_id,
            name=f"{provider}://{repository_name}",
            source_type="repository",
            uploaded_by=user_id,
            metadata_json={
                "provider": provider,
                "repository": repository_name,
                "branch": branch
            }
        )
        source = self.repository.create_source(source)

        # Trigger provider-level repository sync and indexing workflow.
        asyncio.create_task(
            self.orchestrator.sync(
                workspace_id=str(workspace_id),
                source_type="repository",
                source_uri=f"{provider}://{repository_name}",
                branch=branch,
            )
        )
        asyncio.create_task(self.indexing_service.index_source(source.id))

        return source
