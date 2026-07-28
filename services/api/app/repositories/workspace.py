"""
app/repositories/workspace.py

Database operations for Workspaces.
"""
from typing import Tuple, Sequence
from uuid import UUID
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceCreate, WorkspaceUpdate

class WorkspaceRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, organization_id: UUID, payload: WorkspaceCreate) -> Workspace:
        workspace = Workspace(
            organization_id=organization_id,
            name=payload.name,
            slug=payload.slug,
            description=payload.description
        )
        self.session.add(workspace)
        try:
            await self.session.commit()
            await self.session.refresh(workspace)
            return workspace
        except IntegrityError as e:
            await self.session.rollback()
            raise e

    async def get_by_id(self, workspace_id: UUID) -> Workspace | None:
        stmt = select(Workspace).where(Workspace.id == workspace_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_org_and_slug(self, organization_id: UUID, slug: str) -> Workspace | None:
        stmt = select(Workspace).where(
            Workspace.organization_id == organization_id,
            Workspace.slug == slug
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def list_by_organization(self, organization_id: UUID, skip: int = 0, limit: int = 50) -> Tuple[Sequence[Workspace], int]:
        base_stmt = select(Workspace).where(Workspace.organization_id == organization_id)
        
        count_stmt = select(func.count()).select_from(base_stmt.subquery())
        total = (await self.session.execute(count_stmt)).scalar_one()

        stmt = base_stmt.order_by(Workspace.name.asc()).offset(skip).limit(limit)
        items = (await self.session.execute(stmt)).scalars().all()

        return items, total

    async def update(self, workspace: Workspace, payload: WorkspaceUpdate) -> Workspace:
        update_data = payload.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(workspace, field, value)
        
        try:
            await self.session.commit()
            await self.session.refresh(workspace)
            return workspace
        except IntegrityError as e:
            await self.session.rollback()
            raise e

    async def delete(self, workspace: Workspace) -> None:
        await self.session.delete(workspace)
        await self.session.commit()
