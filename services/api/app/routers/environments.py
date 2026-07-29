"""
app/routers/environments.py

FastAPI router for Environments.
"""
from uuid import UUID
from fastapi import APIRouter, Depends, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.models.user import User
from app.dependencies import get_current_user
from app.schemas.environment import EnvironmentCreate, EnvironmentUpdate, EnvironmentRead, EnvironmentList
from app.services.environment import EnvironmentService

router = APIRouter(prefix="/workspaces/{workspace_id}/projects/{project_id}/environments", tags=["environments"])

@router.post("/", response_model=EnvironmentRead, status_code=status.HTTP_201_CREATED)
async def create_environment(
    workspace_id: UUID,
    project_id: UUID,
    payload: EnvironmentCreate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    return await EnvironmentService(session).create_environment(current_user, workspace_id, project_id, payload)

@router.get("/", response_model=EnvironmentList)
async def list_environments(
    workspace_id: UUID,
    project_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    return await EnvironmentService(session).list_environments(current_user, workspace_id, project_id, skip, limit)

@router.get("/{environment_id}", response_model=EnvironmentRead)
async def get_environment(
    workspace_id: UUID,
    project_id: UUID,
    environment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    return await EnvironmentService(session).get_environment(current_user, workspace_id, project_id, environment_id)

@router.patch("/{environment_id}", response_model=EnvironmentRead)
async def update_environment(
    workspace_id: UUID,
    project_id: UUID,
    environment_id: UUID,
    payload: EnvironmentUpdate,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    return await EnvironmentService(session).update_environment(current_user, workspace_id, project_id, environment_id, payload)

@router.delete("/{environment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_environment(
    workspace_id: UUID,
    project_id: UUID,
    environment_id: UUID,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db)
):
    await EnvironmentService(session).delete_environment(current_user, workspace_id, project_id, environment_id)
