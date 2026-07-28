"""
app/schemas/workspace.py

Pydantic schemas for the Workspace domain.
"""
from pydantic import BaseModel, ConfigDict, Field
from uuid import UUID
from datetime import datetime
from typing import List

class WorkspaceBase(BaseModel):
    name: str = Field(..., max_length=255, description="The display name of the workspace.")
    slug: str = Field(..., max_length=255, pattern=r"^[a-z0-9\-]+$", description="URL-friendly identifier.")
    description: str | None = Field(None, description="Optional description of the workspace.")

class WorkspaceCreate(WorkspaceBase):
    pass

class WorkspaceUpdate(BaseModel):
    name: str | None = Field(None, max_length=255)
    description: str | None = None
    is_active: bool | None = None

class WorkspaceRead(WorkspaceBase):
    id: UUID
    organization_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class WorkspaceList(BaseModel):
    items: List[WorkspaceRead]
    total: int
    skip: int
    limit: int
