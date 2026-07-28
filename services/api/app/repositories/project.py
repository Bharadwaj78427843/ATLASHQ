"""
app/repositories/project.py

Database repository for the Project domain.
"""
from uuid import UUID
from typing import Tuple, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.project import Project
from app.schemas.project import ProjectCreate, ProjectUpdate

class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, project_id: UUID) -> Project | None:
        result = await self.session.execute(select(Project).where(Project.id == project_id))
        return result.scalar_one_or_none()

    async def list_by_workspace(self, workspace_id: UUID, skip: int = 0, limit: int = 50) -> Tuple[Sequence[Project], int]:
        query = select(Project).where(Project.workspace_id == workspace_id)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar() or 0
        
        # Get items
        items_query = query.order_by(Project.created_at.desc()).offset(skip).limit(limit)
        items = (await self.session.execute(items_query)).scalars().all()
        
        return items, total

    async def create(self, workspace_id: UUID, payload: ProjectCreate) -> Project:
        project = Project(
            workspace_id=workspace_id,
            name=payload.name,
            description=payload.description
        )
        self.session.add(project)
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def update(self, project: Project, payload: ProjectUpdate) -> Project:
        if payload.name is not None:
            project.name = payload.name
        if payload.description is not None:
            project.description = payload.description
        if payload.is_active is not None:
            project.is_active = payload.is_active
            
        await self.session.commit()
        await self.session.refresh(project)
        return project

    async def delete(self, project: Project) -> None:
        await self.session.delete(project)
        await self.session.commit()
