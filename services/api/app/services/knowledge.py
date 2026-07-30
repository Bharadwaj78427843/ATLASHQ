import asyncio
import os
import shutil
import uuid
from datetime import datetime, timezone
from uuid import UUID

from fastapi import UploadFile

from app.ai.interfaces.document import DocumentRef
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.models.knowledge import IndexJob, KnowledgeDocument, KnowledgeSource
from app.models.workspace import Workspace
from app.repositories.knowledge import KnowledgeRepository
from app.schemas.knowledge import SearchResponse, SearchResultSnippet
from app.core.config import get_settings
from app.services.git_service import GitCloneService
from app.services.repository_indexer import RepositoryIndexer

class StorageService:
    def __init__(self, base_dir: str = None):
        settings = get_settings()
        self.base_dir = base_dir or settings.STORAGE_BASE_PATH
        self.repositories_dir = os.path.join(self.base_dir, "repositories")
        os.makedirs(self.base_dir, exist_ok=True)
        os.makedirs(self.repositories_dir, exist_ok=True)

    def save_file(self, file: UploadFile, source_id: UUID) -> str:
        source_dir = os.path.join(self.base_dir, str(source_id))
        os.makedirs(source_dir, exist_ok=True)
        file_path = os.path.join(source_dir, file.filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        
        return file_path

    def get_repository_path(self, organization_id: str | UUID, workspace_id: str | UUID, repository_name: str) -> str:
        """Returns the local path where a repository should be cloned."""
        safe_repo_name = repository_name.replace("/", "_").replace("\\", "_")
        repo_path = os.path.join(self.repositories_dir, str(organization_id), str(workspace_id), safe_repo_name)
        os.makedirs(repo_path, exist_ok=True)
        return repo_path


class IndexingService:
    def __init__(self, repository: KnowledgeRepository, orchestrator: KnowledgeOrchestrator, git_service: GitCloneService, indexer: RepositoryIndexer, storage_service: StorageService):
        self.repository = repository
        self.orchestrator = orchestrator
        self.git_service = git_service
        self.indexer = indexer
        self.storage_service = storage_service

    async def index_source(self, source_id: UUID):
        source = self.repository.get_source(source_id)
        if not source:
            return

        if source.source_type == "repository":
            await self._index_repository(source)
        else:
            await self._index_document(source)

    async def _index_document(self, source: KnowledgeSource):
        job = self.repository.create_index_job(
            IndexJob(source_id=source.id, status="running", started_at=datetime.now(timezone.utc))
        )
        self.repository.update_source_status(source.id, "indexing")

        try:
            document_name = source.name
            document_ref = DocumentRef(
                id=str(source.id),
                name=document_name,
                uri=source.storage_path or f"source://{source.id}",
                mime_type="application/octet-stream",
                metadata={"workspace_id": str(source.workspace_id), "project_id": str(source.project_id) if source.project_id else None},
            )
            await self.orchestrator.ingest(document_ref, collection=str(source.workspace_id))

            self.repository.update_index_job(job.id, "completed", progress=1.0)
            self.repository.update_source_status(source.id, "ready")
        except Exception as exc:  # noqa: BLE001
            self._handle_index_error(source.id, job.id, exc)

    async def _index_repository(self, source: KnowledgeSource):
        job = self.repository.create_index_job(
            IndexJob(source_id=source.id, status="cloning", started_at=datetime.now(timezone.utc))
        )
        self.repository.update_source_status(source.id, "cloning")
        
        try:
            metadata = source.metadata_json or {}
            provider = metadata.get("provider", "github")
            repo_name = metadata.get("repository")
            url = f"https://github.com/{repo_name}"

            # Get org id from workspace
            workspace = self.repository.db.query(Workspace).filter(Workspace.id == source.workspace_id).first()
            org_id = workspace.organization_id if workspace else "unknown_org"

            target_path = self.storage_service.get_repository_path(org_id, source.workspace_id, repo_name)
            
            # Clone or Pull
            clone_result = await self.git_service.clone_or_pull(url, target_path)

            self.repository.update_source_status(source.id, "indexing")
            self.repository.update_index_job(job.id, "indexing", progress=0.5)

            # Analyze the repository
            repo_metadata = self.indexer.analyze(target_path, provider, url, clone_result.default_branch)
            
            # Store metadata
            source.metadata_json = repo_metadata.model_dump(mode="json")

            self.repository.update_index_job(job.id, "completed", progress=1.0)
            self.repository.update_source_status(source.id, "ready")
            self.repository.db.commit()

        except Exception as exc:
            self._handle_index_error(source.id, job.id, exc)

    def _handle_index_error(self, source_id: UUID, job_id: UUID, exc: Exception):
        self.repository.update_index_job(job_id, "failed", progress=0.0)
        self.repository.update_source_status(source_id, "failed")
        failed = self.repository.db.query(IndexJob).filter(IndexJob.id == job_id).first()
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
    def __init__(self, repository: KnowledgeRepository, indexing_service: IndexingService):
        self.repository = repository
        self.indexing_service = indexing_service
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

        # Create Source record in VALIDATING status
        source = KnowledgeSource(
            workspace_id=workspace_id,
            project_id=project_id,
            name=f"{provider}://{repository_name}",
            source_type="repository",
            uploaded_by=user_id,
            status="validating",
            metadata_json={
                "provider": provider,
                "repository": repository_name,
                "branch": branch
            }
        )
        source = self.repository.create_source(source)

        # Trigger indexing workflow
        asyncio.create_task(self.indexing_service.index_source(source.id))

        return source

    async def sync_repository(self, source_id: UUID) -> KnowledgeSource:
        source = self.repository.get_source(source_id)
        if not source:
            raise ValueError("Knowledge source not found")
            
        if source.source_type != "repository":
            raise ValueError("Source is not a repository")

        if source.status in ["validating", "cloning", "indexing"]:
            raise ValueError("Repository sync is already in progress")

        # Set status to validating to kick off the flow
        self.repository.update_source_status(source.id, "validating")

        # Trigger indexing workflow
        asyncio.create_task(self.indexing_service.index_source(source.id))

        return source
