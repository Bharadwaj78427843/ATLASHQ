"""
app/routers/organizations.py

ATLAS-011 — Organization API endpoints.

All routes require authentication (get_current_user dependency).
Owner-only operations (update, delete) are enforced in OrganizationService.

Routes:
  POST   /organizations/          — Create organization
  GET    /organizations/          — List active organizations
  GET    /organizations/me        — My organizations (owned)
  GET    /organizations/{org_id}  — Get single organization
  PATCH  /organizations/{org_id}  — Update (owner only)
  DELETE /organizations/{org_id}  — Soft delete (owner only)
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationList,
    OrganizationRead,
    OrganizationUpdate,
)
from app.services.organization import OrganizationService

router = APIRouter(prefix="/organizations", tags=["organizations"])


def _svc(session: AsyncSession = Depends(get_db)) -> OrganizationService:
    """Dependency factory — keeps route signatures concise."""
    return OrganizationService(session)


@router.post(
    "/",
    response_model=OrganizationRead,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new organization",
)
async def create_organization(
    payload: OrganizationCreate,
    current_user: User = Depends(get_current_user),
    svc: OrganizationService = Depends(_svc),
) -> OrganizationRead:
    return await svc.create(payload, current_user)


@router.get(
    "/",
    response_model=OrganizationList,
    summary="List all active organizations",
)
async def list_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    svc: OrganizationService = Depends(_svc),
) -> OrganizationList:
    return await svc.list_organizations(skip=skip, limit=limit)


@router.get(
    "/me",
    response_model=OrganizationList,
    summary="List organizations I own",
)
async def list_my_organizations(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    svc: OrganizationService = Depends(_svc),
) -> OrganizationList:
    return await svc.list_my_organizations(current_user, skip=skip, limit=limit)


@router.get(
    "/{org_id}",
    response_model=OrganizationRead,
    summary="Get a single organization by ID",
)
async def get_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    svc: OrganizationService = Depends(_svc),
) -> OrganizationRead:
    return await svc.get_by_id(org_id)


@router.patch(
    "/{org_id}",
    response_model=OrganizationRead,
    summary="Update an organization (owner only)",
)
async def update_organization(
    org_id: UUID,
    payload: OrganizationUpdate,
    current_user: User = Depends(get_current_user),
    svc: OrganizationService = Depends(_svc),
) -> OrganizationRead:
    return await svc.update(org_id, payload, current_user)


@router.delete(
    "/{org_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Soft delete an organization (owner only)",
)
async def delete_organization(
    org_id: UUID,
    current_user: User = Depends(get_current_user),
    svc: OrganizationService = Depends(_svc),
) -> None:
    await svc.delete(org_id, current_user)
