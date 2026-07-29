from pydantic import BaseModel, ConfigDict
from uuid import UUID
from datetime import datetime
from typing import Optional, List, Any

# Knowledge Source Schemas
class KnowledgeSourceBase(BaseModel):
    name: str
    source_type: str
    storage_path: Optional[str] = None
    size_bytes: Optional[int] = None
    metadata_json: Optional[Any] = None

class KnowledgeSourceCreate(KnowledgeSourceBase):
    pass

class RepositoryConnectRequest(BaseModel):
    workspace_id: UUID
    provider: str
    repository: str
    branch: str
    project_id: Optional[UUID] = None

class KnowledgeSourceResponse(KnowledgeSourceBase):
    id: UUID
    workspace_id: UUID
    project_id: Optional[UUID]
    status: str
    uploaded_by: UUID
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# Knowledge Document Schemas
class KnowledgeDocumentResponse(BaseModel):
    id: UUID
    source_id: UUID
    filename: str
    mime_type: str
    pages: Optional[int] = None
    
    model_config = ConfigDict(from_attributes=True)


# Index Job Schemas
class IndexJobResponse(BaseModel):
    id: UUID
    source_id: UUID
    status: str
    progress: float
    started_at: Optional[datetime]
    completed_at: Optional[datetime]
    error_message: Optional[str]

    model_config = ConfigDict(from_attributes=True)


# Search Request Schemas
class SearchQuery(BaseModel):
    query: str
    limit: int = 10
    project_id: Optional[UUID] = None

class SearchResultSnippet(BaseModel):
    source_id: UUID
    source_name: str
    document_id: UUID
    filename: str
    content: str
    score: float

class SearchResponse(BaseModel):
    query: str
    results: List[SearchResultSnippet]
