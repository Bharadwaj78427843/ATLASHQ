"""
app/services/organization_membership.py

OrganizationMembershipService — Business logic for Organization Membership.
"""
from uuid import UUID
from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization_member import OrganizationMember, MemberRole, MemberStatus
from app.models.organization import Organization
from app.models.user import User
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.organization import OrganizationRepository
from app.repositories.user import UserRepository
from app.schemas.organization_member import (
    OrganizationMemberRead,
    OrganizationMemberList,
    InviteMemberRequest,
    UpdateMemberRole,
    TransferOwnershipRequest,
)


class OrganizationMembershipService:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._repo = OrganizationMemberRepository(session)
        self._org_repo = OrganizationRepository(session)
        self._user_repo = UserRepository(session)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _to_read(self, member: OrganizationMember) -> OrganizationMemberRead:
        return OrganizationMemberRead.model_validate(member)

    async def _get_org_or_404(self, org_id: UUID) -> Organization:
        org = await self._org_repo.get_by_id(org_id)
        if org is None or not org.is_active:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
        return org

    async def _get_member_or_404(self, member_id: UUID) -> OrganizationMember:
        member = await self._repo.get_by_id(member_id)
        if member is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
        return member

    async def _get_caller_membership(self, org_id: UUID, user_id: UUID) -> OrganizationMember:
        caller = await self._repo.get_by_org_and_user(org_id, user_id)
        if not caller or caller.status != MemberStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You do not have access to this organization")
        return caller

    def _assert_can_manage(self, caller: OrganizationMember, target_role: MemberRole | None = None) -> None:
        if caller.role not in (MemberRole.OWNER, MemberRole.ADMIN):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Requires ADMIN or OWNER role")
        
        # Prevent privilege escalation: Admin cannot manage/invite Owners
        if caller.role == MemberRole.ADMIN and target_role == MemberRole.OWNER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot grant or manage OWNER role")

    def _assert_can_manage_target(self, caller: OrganizationMember, target: OrganizationMember) -> None:
        self._assert_can_manage(caller)
        if caller.role == MemberRole.ADMIN and target.role == MemberRole.OWNER:
             raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins cannot modify OWNER members")

    # ── Operations ────────────────────────────────────────────────────────────

    async def invite_member(self, org_id: UUID, payload: InviteMemberRequest, current_user: User) -> OrganizationMemberRead:
        await self._get_org_or_404(org_id)
        caller = await self._get_caller_membership(org_id, current_user.id)
        self._assert_can_manage(caller, payload.role)

        target_user = await self._user_repo.get_by_email(payload.email)
        if not target_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User with this email not found")

        if await self._repo.exists(org_id, target_user.id):
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member or invited")

        try:
            member = await self._repo.create(
                org_id=org_id,
                user_id=target_user.id,
                role=payload.role,
                status=MemberStatus.INVITED,
                invited_by_id=current_user.id,
            )
        except IntegrityError:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User is already a member or invited")

        return self._to_read(member)

    async def list_members(self, org_id: UUID, current_user: User, skip: int = 0, limit: int = 50) -> OrganizationMemberList:
        await self._get_org_or_404(org_id)
        await self._get_caller_membership(org_id, current_user.id) # Just ensure they have access

        items, total = await self._repo.list_by_organization(org_id, skip=skip, limit=limit)
        return OrganizationMemberList(
            items=[self._to_read(m) for m in items],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_member(self, org_id: UUID, member_id: UUID, current_user: User) -> OrganizationMemberRead:
        await self._get_org_or_404(org_id)
        await self._get_caller_membership(org_id, current_user.id)
        
        member = await self._get_member_or_404(member_id)
        if member.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found in this organization")
            
        return self._to_read(member)

    async def update_role(self, org_id: UUID, member_id: UUID, payload: UpdateMemberRole, current_user: User) -> OrganizationMemberRead:
        await self._get_org_or_404(org_id)
        caller = await self._get_caller_membership(org_id, current_user.id)
        
        member = await self._get_member_or_404(member_id)
        if member.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")
            
        self._assert_can_manage_target(caller, member)
        self._assert_can_manage(caller, payload.role)

        # Prevent removing the last owner via role downgrade
        if member.role == MemberRole.OWNER and payload.role != MemberRole.OWNER:
            owner_count = await self._repo.count_owners(org_id)
            if owner_count <= 1:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot downgrade the last owner")

        member.role = payload.role
        updated = await self._repo.update(member)
        return self._to_read(updated)

    async def remove_member(self, org_id: UUID, member_id: UUID, current_user: User) -> None:
        await self._get_org_or_404(org_id)
        caller = await self._get_caller_membership(org_id, current_user.id)
        
        member = await self._get_member_or_404(member_id)
        if member.organization_id != org_id:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member not found")

        # Users can leave voluntarily, otherwise require manage rights
        is_self = member.user_id == current_user.id
        if not is_self:
            self._assert_can_manage_target(caller, member)

        if member.role == MemberRole.OWNER:
            owner_count = await self._repo.count_owners(org_id)
            if owner_count <= 1:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot remove the last owner")

        if is_self and member.status == MemberStatus.ACTIVE:
            member.status = MemberStatus.LEFT
            await self._repo.update(member)
        else:
            await self._repo.soft_delete(member)

    async def accept_invitation(self, org_id: UUID, member_id: UUID, current_user: User) -> OrganizationMemberRead:
        await self._get_org_or_404(org_id)
        member = await self._get_member_or_404(member_id)
        
        if member.organization_id != org_id or member.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your invitation")
            
        if member.status != MemberStatus.INVITED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation is not pending")

        member.status = MemberStatus.ACTIVE
        member.joined_at = datetime.now(timezone.utc)
        updated = await self._repo.update(member)
        return self._to_read(updated)

    async def reject_invitation(self, org_id: UUID, member_id: UUID, current_user: User) -> None:
        await self._get_org_or_404(org_id)
        member = await self._get_member_or_404(member_id)
        
        if member.organization_id != org_id or member.user_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not your invitation")
            
        if member.status != MemberStatus.INVITED:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invitation is not pending")

        await self._repo.soft_delete(member)

    async def transfer_ownership(self, org_id: UUID, payload: TransferOwnershipRequest, current_user: User) -> None:
        org = await self._get_org_or_404(org_id)
        caller = await self._get_caller_membership(org_id, current_user.id)
        
        if caller.role != MemberRole.OWNER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owners can transfer ownership")
            
        target_member = await self._repo.get_by_org_and_user(org_id, payload.target_user_id)
        if not target_member or target_member.status != MemberStatus.ACTIVE:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Target user is not an active member")

        # Atomic swap
        org.owner_id = target_member.user_id
        target_member.role = MemberRole.OWNER
        caller.role = MemberRole.ADMIN
        
        await self._session.commit()
