"""
app/repositories/environment.py

Database repository for the Environment domain.
"""
from uuid import UUID
from typing import Tuple, Sequence
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.environment import Environment
from app.schemas.environment import EnvironmentCreate, EnvironmentUpdate

class EnvironmentRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, environment_id: UUID) -> Environment | None:
        result = await self.session.execute(select(Environment).where(Environment.id == environment_id))
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: UUID, skip: int = 0, limit: int = 50) -> Tuple[Sequence[Environment], int]:
        query = select(Environment).where(Environment.project_id == project_id)
        
        count_query = select(func.count()).select_from(query.subquery())
        total = (await self.session.execute(count_query)).scalar() or 0
        
        items_query = query.order_by(Environment.created_at.desc()).offset(skip).limit(limit)
        items = (await self.session.execute(items_query)).scalars().all()
        
        return items, total

    async def create(self, project_id: UUID, payload: EnvironmentCreate) -> Environment:
        env = Environment(
            project_id=project_id,
            name=payload.name,
            type=payload.type
        )
        self.session.add(env)
        await self.session.commit()
        await self.session.refresh(env)
        return env

    async def update(self, env: Environment, payload: EnvironmentUpdate) -> Environment:
        if payload.name is not None:
            env.name = payload.name
        if payload.type is not None:
            env.type = payload.type
        if payload.is_active is not None:
            env.is_active = payload.is_active
            
        await self.session.commit()
        await self.session.refresh(env)
        return env

    async def delete(self, env: Environment) -> None:
        await self.session.delete(env)
        await self.session.commit()
