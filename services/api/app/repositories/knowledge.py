from typing import List, Optional, Sequence
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.knowledge import KnowledgeSource, KnowledgeDocument, IndexJob

class KnowledgeRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_source(self, source: KnowledgeSource) -> KnowledgeSource:
        self.db.add(source)
        await self.db.commit()
        await self.db.refresh(source)
        return source

    async def get_source(self, source_id: UUID) -> Optional[KnowledgeSource]:
        result = await self.db.execute(select(KnowledgeSource).where(KnowledgeSource.id == source_id))
        return result.scalar_one_or_none()

    async def get_sources_by_workspace(self, workspace_id: UUID) -> Sequence[KnowledgeSource]:
        result = await self.db.execute(select(KnowledgeSource).where(KnowledgeSource.workspace_id == workspace_id))
        return result.scalars().all()

    async def update_source_status(self, source_id: UUID, status: str) -> Optional[KnowledgeSource]:
        source = await self.get_source(source_id)
        if source:
            source.status = status
            await self.db.commit()
            await self.db.refresh(source)
        return source

    async def delete_source(self, source_id: UUID) -> bool:
        source = await self.get_source(source_id)
        if source:
            await self.db.delete(source)
            await self.db.commit()
            return True
        return False

    async def create_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def create_index_job(self, job: IndexJob) -> IndexJob:
        self.db.add(job)
        await self.db.commit()
        await self.db.refresh(job)
        return job

    async def get_index_jobs_by_source(self, source_id: UUID) -> Sequence[IndexJob]:
        result = await self.db.execute(select(IndexJob).where(IndexJob.source_id == source_id))
        return result.scalars().all()

    async def update_index_job(self, job_id: UUID, status: str, progress: float) -> Optional[IndexJob]:
        result = await self.db.execute(select(IndexJob).where(IndexJob.id == job_id))
        job = result.scalar_one_or_none()
        if job:
            job.status = status
            job.progress = progress
            await self.db.commit()
            await self.db.refresh(job)
        return job
