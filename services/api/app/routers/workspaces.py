"""
app/routers/workspaces.py

API router for the Workspace domain.
Mounted under /organizations/{org_id}/workspaces.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.services.workspace import WorkspaceService
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate, WorkspaceRead, WorkspaceList

router = APIRouter(prefix="/organizations/{org_id}/workspaces", tags=["Workspaces"])

@router.post("", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED)
@router.post("/", response_model=WorkspaceRead, status_code=status.HTTP_201_CREATED, include_in_schema=False)
async def create_workspace(
    org_id: UUID,
    payload: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new workspace within an organization."""
    return await WorkspaceService(db).create_workspace(current_user, org_id, payload)

@router.get("", response_model=WorkspaceList)
@router.get("/", response_model=WorkspaceList, include_in_schema=False)
async def list_workspaces(
    org_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List workspaces in an organization."""
    return await WorkspaceService(db).list_workspaces(current_user, org_id, skip, limit)

@router.get("/{workspace_id}", response_model=WorkspaceRead)
async def get_workspace(
    org_id: UUID,
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific workspace."""
    return await WorkspaceService(db).get_workspace(current_user, org_id, workspace_id)

@router.patch("/{workspace_id}", response_model=WorkspaceRead)
async def update_workspace(
    org_id: UUID,
    workspace_id: UUID,
    payload: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a specific workspace."""
    return await WorkspaceService(db).update_workspace(current_user, org_id, workspace_id, payload)

@router.delete("/{workspace_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_workspace(
    org_id: UUID,
    workspace_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a specific workspace."""
    await WorkspaceService(db).delete_workspace(current_user, org_id, workspace_id)
