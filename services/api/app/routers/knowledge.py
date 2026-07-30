from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.db.session import get_db
from app.dependencies import get_current_user
from app.dependencies import get_knowledge_orchestrator
from app.models.user import User
from app.repositories.knowledge import KnowledgeRepository
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.services.knowledge import UploadService, StorageService, IndexingService, SearchService, RepositoryService
from app.services.git_service import GitCloneService
from app.services.repository_indexer import RepositoryIndexer
from app.schemas.knowledge import KnowledgeSourceResponse, IndexJobResponse, SearchQuery, SearchResponse, RepositoryConnectRequest

router = APIRouter(prefix="/knowledge", tags=["knowledge"])

def get_services(
    db: Session = Depends(get_db),
    orchestrator: KnowledgeOrchestrator = Depends(get_knowledge_orchestrator),
):
    repo = KnowledgeRepository(db)
    storage = StorageService()
    git_service = GitCloneService()
    indexer = RepositoryIndexer()
    indexing = IndexingService(repo, orchestrator, git_service, indexer, storage)
    upload = UploadService(repo, storage, indexing)
    search = SearchService(repo, orchestrator)
    repo_service = RepositoryService(repo, indexing)
    return repo, upload, search, repo_service

@router.post("/upload", response_model=KnowledgeSourceResponse)
async def upload_source(
    workspace_id: UUID = Form(...),
    project_id: UUID = Form(None),
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    services: tuple = Depends(get_services)
):
    _, upload_service, _, _ = services
    try:
        source = await upload_service.process_upload(
            file=file,
            workspace_id=workspace_id,
            user_id=current_user.id,
            project_id=project_id
        )
        return source
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/repositories/connect", response_model=KnowledgeSourceResponse)
async def connect_repository(
    request: RepositoryConnectRequest,
    current_user: User = Depends(get_current_user),
    services: tuple = Depends(get_services)
):
    _, _, _, repo_service = services
    try:
        source = await repo_service.connect_repository(
            workspace_id=request.workspace_id,
            user_id=current_user.id,
            provider=request.provider,
            repository_name=request.repository,
            branch=request.branch,
            project_id=request.project_id
        )
        return source
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/repositories/{source_id}/sync", response_model=KnowledgeSourceResponse)
async def sync_repository(
    source_id: UUID,
    current_user: User = Depends(get_current_user),
    services: tuple = Depends(get_services)
):
    _, _, _, repo_service = services
    try:
        source = await repo_service.sync_repository(source_id)
        return source
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        if "already in progress" in str(e):
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/sources", response_model=List[KnowledgeSourceResponse])
def get_sources(
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    services: tuple = Depends(get_services)
):
    repo, _, _, _ = services
    return repo.get_sources_by_workspace(workspace_id)

@router.get("/sources/{source_id}", response_model=KnowledgeSourceResponse)
def get_source(
    source_id: UUID,
    current_user: User = Depends(get_current_user),
    services: tuple = Depends(get_services)
):
    repo, _, _, _ = services
    source = repo.get_source(source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")
    return source

@router.delete("/sources/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_source(
    source_id: UUID,
    current_user: User = Depends(get_current_user),
    services: tuple = Depends(get_services)
):
    repo, _, _, _ = services
    if not repo.delete_source(source_id):
        raise HTTPException(status_code=404, detail="Source not found")

@router.get("/jobs", response_model=List[IndexJobResponse])
def get_jobs(
    source_id: UUID,
    current_user: User = Depends(get_current_user),
    services: tuple = Depends(get_services)
):
    repo, _, _, _ = services
    return repo.get_index_jobs_by_source(source_id)

@router.post("/search", response_model=SearchResponse)
async def search_knowledge(
    workspace_id: UUID,
    query: SearchQuery,
    current_user: User = Depends(get_current_user),
    services: tuple = Depends(get_services)
):
    _, _, search_service, _ = services
    return await search_service.search(query.query, workspace_id, limit=query.limit)
