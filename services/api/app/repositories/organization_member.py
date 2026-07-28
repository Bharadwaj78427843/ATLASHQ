"""
app/repositories/organization_member.py

Pure data-access layer for OrganizationMembership.
Handles all database operations without raising HTTP exceptions.
"""
from typing import Sequence
from uuid import UUID
from datetime import datetime, timezone

from sqlalchemy import select, func, and_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.organization_member import OrganizationMember, MemberRole, MemberStatus


class OrganizationMemberRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_by_id(self, member_id: UUID) -> OrganizationMember | None:
        stmt = (
            select(OrganizationMember)
            .options(selectinload(OrganizationMember.user))
            .where(OrganizationMember.id == member_id, OrganizationMember.deleted_at.is_(None))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_org_and_user(self, org_id: UUID, user_id: UUID) -> OrganizationMember | None:
        stmt = (
            select(OrganizationMember)
            .options(selectinload(OrganizationMember.user))
            .where(
                OrganizationMember.organization_id == org_id,
                OrganizationMember.user_id == user_id,
                OrganizationMember.deleted_at.is_(None)
            )
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists(self, org_id: UUID, user_id: UUID) -> bool:
        stmt = select(func.count()).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.user_id == user_id,
            OrganizationMember.deleted_at.is_(None)
        )
        result = await self._session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def list_by_organization(
        self,
        org_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[OrganizationMember], int]:
        base = select(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.deleted_at.is_(None)
        )
        count_base = select(func.count()).select_from(OrganizationMember).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.deleted_at.is_(None)
        )

        total_result = await self._session.execute(count_base)
        total = total_result.scalar_one() or 0

        stmt = (
            base.options(selectinload(OrganizationMember.user))
            .order_by(OrganizationMember.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        result = await self._session.execute(stmt)
        return result.scalars().all(), total

    async def count_owners(self, org_id: UUID) -> int:
        stmt = select(func.count()).where(
            OrganizationMember.organization_id == org_id,
            OrganizationMember.role == MemberRole.OWNER,
            OrganizationMember.status == MemberStatus.ACTIVE,
            OrganizationMember.deleted_at.is_(None)
        )
        result = await self._session.execute(stmt)
        return result.scalar_one() or 0

    # ── Writes ────────────────────────────────────────────────────────────────

    async def create(
        self,
        org_id: UUID,
        user_id: UUID,
        role: MemberRole,
        status: MemberStatus,
        invited_by_id: UUID | None = None,
        joined_at: datetime | None = None,
    ) -> OrganizationMember:
        member = OrganizationMember(
            organization_id=org_id,
            user_id=user_id,
            role=role,
            status=status,
            invited_by_id=invited_by_id,
            joined_at=joined_at,
        )
        self._session.add(member)
        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise
            
        # Re-fetch to ensure all relationships (like user) are selectinload-ed
        fetched = await self.get_by_id(member.id)
        if not fetched:
            raise RuntimeError("Failed to fetch newly created member")
        return fetched

    async def update(self, member: OrganizationMember) -> OrganizationMember:
        try:
            await self._session.commit()
        except IntegrityError:
            await self._session.rollback()
            raise
            
        fetched = await self.get_by_id(member.id)
        if not fetched:
            raise RuntimeError("Failed to fetch updated member")
        return fetched

    async def soft_delete(self, member: OrganizationMember) -> None:
        member.deleted_at = datetime.now(timezone.utc)
        await self._session.commit()
