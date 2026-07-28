"""
app/repositories/organization.py

OrganizationRepository — pure data access, zero business logic.

Rules:
  - Never raises HTTP exceptions.
  - Never makes business decisions.
  - All commits are controlled by the caller (service layer).
  - IntegrityError propagates to the service which decides the HTTP status.
"""
from typing import Sequence
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.organization import Organization
from app.schemas.organization import OrganizationCreate, OrganizationUpdate


class OrganizationRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    # ── Reads ─────────────────────────────────────────────────────────────────

    async def get_by_id(self, org_id: UUID) -> Organization | None:
        stmt = select(Organization).where(Organization.id == org_id)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Organization | None:
        stmt = select(Organization).where(Organization.slug == slug)
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_slug(self, slug: str) -> bool:
        stmt = select(func.count()).where(Organization.slug == slug)
        result = await self._session.execute(stmt)
        return (result.scalar_one() or 0) > 0

    async def list(
        self,
        skip: int = 0,
        limit: int = 50,
        active_only: bool = True,
    ) -> tuple[Sequence[Organization], int]:
        base = select(Organization)
        count_base = select(func.count()).select_from(Organization)
        if active_only:
            base = base.where(Organization.is_active == True)  # noqa: E712
            count_base = count_base.where(Organization.is_active == True)  # noqa: E712

        total_result = await self._session.execute(count_base)
        total = total_result.scalar_one() or 0

        stmt = base.order_by(Organization.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total

    async def list_by_owner(
        self,
        owner_id: UUID,
        skip: int = 0,
        limit: int = 50,
    ) -> tuple[Sequence[Organization], int]:
        base = select(Organization).where(Organization.owner_id == owner_id)
        count_base = select(func.count()).select_from(Organization).where(
            Organization.owner_id == owner_id
        )

        total_result = await self._session.execute(count_base)
        total = total_result.scalar_one() or 0

        stmt = base.order_by(Organization.created_at.desc()).offset(skip).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all(), total

    # ── Writes ────────────────────────────────────────────────────────────────

    async def create(
        self,
        payload: OrganizationCreate,
        owner_id: UUID,
    ) -> Organization:
        """
        Persist a new organization.
        Raises IntegrityError on duplicate slug (unique constraint).
        The service layer translates this to HTTP 409.
        """
        org = Organization(
            name=payload.name,
            slug=payload.slug,
            description=payload.description,
            logo_url=payload.logo_url,
            website=payload.website,
            owner_id=owner_id,
            is_active=True,
        )
        self._session.add(org)
        try:
            await self._session.commit()
            await self._session.refresh(org)
        except IntegrityError:
            await self._session.rollback()
            raise
        return org

    async def update(
        self,
        org: Organization,
        payload: OrganizationUpdate,
    ) -> Organization:
        """
        Apply partial update to an already-fetched Organization instance.
        Caller is responsible for authorization checks.
        """
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(org, field, value)
        try:
            await self._session.commit()
            await self._session.refresh(org)
        except IntegrityError:
            await self._session.rollback()
            raise
        return org

    async def soft_delete(self, org: Organization) -> Organization:
        """Mark the organization as inactive (soft delete)."""
        org.is_active = False
        await self._session.commit()
        await self._session.refresh(org)
        return org
