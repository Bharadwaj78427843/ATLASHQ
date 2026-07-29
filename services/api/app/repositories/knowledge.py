from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select

from app.models.knowledge import KnowledgeSource, KnowledgeDocument, IndexJob

class KnowledgeRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_source(self, source: KnowledgeSource) -> KnowledgeSource:
        self.db.add(source)
        self.db.commit()
        self.db.refresh(source)
        return source

    def get_source(self, source_id: UUID) -> Optional[KnowledgeSource]:
        return self.db.query(KnowledgeSource).filter(KnowledgeSource.id == source_id).first()

    def get_sources_by_workspace(self, workspace_id: UUID) -> List[KnowledgeSource]:
        return self.db.query(KnowledgeSource).filter(KnowledgeSource.workspace_id == workspace_id).all()

    def update_source_status(self, source_id: UUID, status: str) -> Optional[KnowledgeSource]:
        source = self.get_source(source_id)
        if source:
            source.status = status
            self.db.commit()
            self.db.refresh(source)
        return source

    def delete_source(self, source_id: UUID) -> bool:
        source = self.get_source(source_id)
        if source:
            self.db.delete(source)
            self.db.commit()
            return True
        return False

    def create_document(self, document: KnowledgeDocument) -> KnowledgeDocument:
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def create_index_job(self, job: IndexJob) -> IndexJob:
        self.db.add(job)
        self.db.commit()
        self.db.refresh(job)
        return job

    def get_index_jobs_by_source(self, source_id: UUID) -> List[IndexJob]:
        return self.db.query(IndexJob).filter(IndexJob.source_id == source_id).all()

    def update_index_job(self, job_id: UUID, status: str, progress: float) -> Optional[IndexJob]:
        job = self.db.query(IndexJob).filter(IndexJob.id == job_id).first()
        if job:
            job.status = status
            job.progress = progress
            self.db.commit()
            self.db.refresh(job)
        return job
