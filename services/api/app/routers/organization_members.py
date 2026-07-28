"""
app/routers/organization_members.py

ATLAS-012 — Organization Membership API endpoints.
"""
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.schemas.organization_member import (
    OrganizationMemberList,
    OrganizationMemberRead,
    InviteMemberRequest,
    UpdateMemberRole,
    TransferOwnershipRequest,
)
from app.services.organization_membership import OrganizationMembershipService

router = APIRouter(prefix="/organizations/{org_id}/members", tags=["organization-members"])


def _svc(session: AsyncSession = Depends(get_db)) -> OrganizationMembershipService:
    return OrganizationMembershipService(session)


@router.get("/", response_model=OrganizationMemberList, summary="List members")
async def list_members(
    org_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    svc: OrganizationMembershipService = Depends(_svc),
) -> OrganizationMemberList:
    return await svc.list_members(org_id, current_user, skip=skip, limit=limit)


@router.post("/invite", response_model=OrganizationMemberRead, status_code=status.HTTP_201_CREATED, summary="Invite user")
async def invite_member(
    org_id: UUID,
    payload: InviteMemberRequest,
    current_user: User = Depends(get_current_user),
    svc: OrganizationMembershipService = Depends(_svc),
) -> OrganizationMemberRead:
    return await svc.invite_member(org_id, payload, current_user)


@router.get("/{member_id}", response_model=OrganizationMemberRead, summary="Get member details")
async def get_member(
    org_id: UUID,
    member_id: UUID,
    current_user: User = Depends(get_current_user),
    svc: OrganizationMembershipService = Depends(_svc),
) -> OrganizationMemberRead:
    return await svc.get_member(org_id, member_id, current_user)


@router.patch("/{member_id}", response_model=OrganizationMemberRead, summary="Update member role")
async def update_member_role(
    org_id: UUID,
    member_id: UUID,
    payload: UpdateMemberRole,
    current_user: User = Depends(get_current_user),
    svc: OrganizationMembershipService = Depends(_svc),
) -> OrganizationMemberRead:
    return await svc.update_role(org_id, member_id, payload, current_user)


@router.delete("/{member_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remove or leave")
async def remove_member(
    org_id: UUID,
    member_id: UUID,
    current_user: User = Depends(get_current_user),
    svc: OrganizationMembershipService = Depends(_svc),
) -> None:
    await svc.remove_member(org_id, member_id, current_user)


@router.post("/{member_id}/accept", response_model=OrganizationMemberRead, summary="Accept invite")
async def accept_invitation(
    org_id: UUID,
    member_id: UUID,
    current_user: User = Depends(get_current_user),
    svc: OrganizationMembershipService = Depends(_svc),
) -> OrganizationMemberRead:
    return await svc.accept_invitation(org_id, member_id, current_user)


@router.post("/{member_id}/reject", status_code=status.HTTP_204_NO_CONTENT, summary="Reject invite")
async def reject_invitation(
    org_id: UUID,
    member_id: UUID,
    current_user: User = Depends(get_current_user),
    svc: OrganizationMembershipService = Depends(_svc),
) -> None:
    await svc.reject_invitation(org_id, member_id, current_user)


@router.post("/transfer-owner", status_code=status.HTTP_204_NO_CONTENT, summary="Transfer ownership")
async def transfer_ownership(
    org_id: UUID,
    payload: TransferOwnershipRequest,
    current_user: User = Depends(get_current_user),
    svc: OrganizationMembershipService = Depends(_svc),
) -> None:
    await svc.transfer_ownership(org_id, payload, current_user)
