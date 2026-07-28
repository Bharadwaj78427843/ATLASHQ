"""
app/routers/projects.py

API router for the Project domain.
Mounted under /workspaces/{workspace_id}/projects.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.services.project import ProjectService
from app.schemas.project import ProjectCreate, ProjectUpdate, ProjectRead, ProjectList

router = APIRouter(prefix="/workspaces/{workspace_id}/projects", tags=["Projects"])

@router.post("/", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project(
    workspace_id: UUID,
    payload: ProjectCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Create a new project within a workspace."""
    return await ProjectService(db).create_project(current_user, workspace_id, payload)

@router.get("/", response_model=ProjectList)
async def list_projects(
    workspace_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """List projects in a workspace."""
    return await ProjectService(db).list_projects(current_user, workspace_id, skip, limit)

@router.get("/{project_id}", response_model=ProjectRead)
async def get_project(
    workspace_id: UUID,
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get a specific project."""
    return await ProjectService(db).get_project(current_user, workspace_id, project_id)

@router.patch("/{project_id}", response_model=ProjectRead)
async def update_project(
    workspace_id: UUID,
    project_id: UUID,
    payload: ProjectUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update a specific project."""
    return await ProjectService(db).update_project(current_user, workspace_id, project_id, payload)

@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_project(
    workspace_id: UUID,
    project_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Delete a specific project."""
    await ProjectService(db).delete_project(current_user, workspace_id, project_id)
