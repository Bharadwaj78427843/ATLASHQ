"""
app/services/organization.py

OrganizationService — all business logic for the Organization domain.

Business rules enforced here:
  1. Any authenticated user can create an organization.
  2. Creator is automatically set as owner.
  3. Duplicate slug → HTTP 409 Conflict.
  4. Inactive organizations cannot be modified (HTTP 403).
  5. Only the owner can update or delete.
  6. Delete is soft delete (is_active=False).
  7. Listing returns only active organizations by default.

The repository never raises HTTP exceptions.
This service translates repository outcomes into HTTP semantics.
"""
from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.models.user import User
from app.repositories.organization import OrganizationRepository
from app.schemas.organization import (
    OrganizationCreate,
    OrganizationList,
    OrganizationRead,
    OrganizationUpdate,
)


class OrganizationService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = OrganizationRepository(session)

    # ── Helpers ───────────────────────────────────────────────────────────────

    def _to_read(self, org: Organization) -> OrganizationRead:
        return OrganizationRead.model_validate(org)

    async def _get_active_or_404(self, org_id: UUID) -> Organization:
        org = await self._repo.get_by_id(org_id)
        if org is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Organization not found",
            )
        return org

    def _assert_owner(self, org: Organization, user: User) -> None:
        """Raise 403 if the requesting user is not the organization owner."""
        if org.owner_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this organization",
            )

    def _assert_active(self, org: Organization) -> None:
        """Raise 403 if the organization is inactive (soft-deleted)."""
        if not org.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="This organization is inactive and cannot be modified",
            )

    # ── Operations ────────────────────────────────────────────────────────────

    async def create(
        self,
        payload: OrganizationCreate,
        current_user: User,
    ) -> OrganizationRead:
        """
        Create a new organization owned by *current_user*.
        Also creates the corresponding OrganizationMember (OWNER/ACTIVE).
        """
        # Pre-flight uniqueness check for a clean 409
        if await self._repo.exists_slug(payload.slug):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Slug '{payload.slug}' is already taken",
            )
        try:
            org = await self._repo.create(payload, owner_id=current_user.id)
            
            # Create the owner membership
            from app.models.organization_member import OrganizationMember, MemberRole, MemberStatus
            from app.repositories.organization_member import OrganizationMemberRepository
            from datetime import datetime, timezone
            
            member_repo = OrganizationMemberRepository(self._repo._session)
            await member_repo.create(
                org_id=org.id,
                user_id=current_user.id,
                role=MemberRole.OWNER,
                status=MemberStatus.ACTIVE,
                joined_at=datetime.now(timezone.utc)
            )
            
        except IntegrityError:
            # Race condition
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Slug '{payload.slug}' is already taken",
            )
        return self._to_read(org)

    async def list_organizations(
        self,
        skip: int = 0,
        limit: int = 50,
    ) -> OrganizationList:
        items, total = await self._repo.list(skip=skip, limit=limit, active_only=True)
        return OrganizationList(
            items=[self._to_read(o) for o in items],
            total=total,
            skip=skip,
            limit=limit,
        )

    async def get_by_id(self, org_id: UUID) -> OrganizationRead:
        org = await self._get_active_or_404(org_id)
        return self._to_read(org)

    async def update(
        self,
        org_id: UUID,
        payload: OrganizationUpdate,
        current_user: User,
    ) -> OrganizationRead:
        org = await self._get_active_or_404(org_id)
        self._assert_active(org)
        self._assert_owner(org, current_user)
        try:
            updated = await self._repo.update(org, payload)
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Update conflicts with an existing organization",
            )
        return self._to_read(updated)

    async def delete(
        self,
        org_id: UUID,
        current_user: User,
    ) -> None:
        """Soft delete — sets is_active=False. Returns 204 No Content."""
        org = await self._get_active_or_404(org_id)
        self._assert_active(org)
        self._assert_owner(org, current_user)
        await self._repo.soft_delete(org)

    async def list_my_organizations(
        self,
        current_user: User,
        skip: int = 0,
        limit: int = 50,
    ) -> OrganizationList:
        items, total = await self._repo.list_by_owner(
            owner_id=current_user.id, skip=skip, limit=limit
        )
        return OrganizationList(
            items=[self._to_read(o) for o in items],
            total=total,
            skip=skip,
            limit=limit,
        )
