import uuid
from datetime import datetime
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, BigInteger, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.base import Base

class KnowledgeSource(Base):
    __tablename__ = "knowledge_sources"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    workspace_id = Column(UUID(as_uuid=True), ForeignKey("workspaces.id"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id"), nullable=True)
    name = Column(String, nullable=False)
    source_type = Column(String, nullable=False) # e.g. "document", "repository", "url"
    storage_path = Column(String, nullable=True)
    metadata_json = Column(JSONB, nullable=True)
    status = Column(String, nullable=False, default="pending") # "pending", "indexing", "ready", "failed"
    size_bytes = Column(BigInteger, nullable=True)
    uploaded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    workspace = relationship("Workspace")
    project = relationship("Project")
    uploader = relationship("User")
    documents = relationship("KnowledgeDocument", back_populates="source", cascade="all, delete-orphan")
    jobs = relationship("IndexJob", back_populates="source", cascade="all, delete-orphan")


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_sources.id"), nullable=False)
    filename = Column(String, nullable=False)
    mime_type = Column(String, nullable=False)
    checksum = Column(String, nullable=True)
    pages = Column(Integer, nullable=True)
    metadata_json = Column(JSONB, nullable=True)

    source = relationship("KnowledgeSource", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_documents.id"), nullable=False)
    chunk_index = Column(Integer, nullable=False)
    content = Column(String, nullable=False)
    token_count = Column(Integer, nullable=True)
    embedding_id = Column(String, nullable=True)

    document = relationship("KnowledgeDocument", back_populates="chunks")
    embeddings = relationship("Embedding", back_populates="chunk", cascade="all, delete-orphan")


class Embedding(Base):
    __tablename__ = "embeddings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    chunk_id = Column(UUID(as_uuid=True), ForeignKey("document_chunks.id"), nullable=False)
    provider = Column(String, nullable=False) # e.g. "openai"
    model = Column(String, nullable=False) # e.g. "text-embedding-3-small"
    vector_dimension = Column(Integer, nullable=False)
    vector_store_key = Column(String, nullable=False) # Key to find vector in pgvector/qdrant/pinecone

    chunk = relationship("DocumentChunk", back_populates="embeddings")


class IndexJob(Base):
    __tablename__ = "index_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("knowledge_sources.id"), nullable=False)
    status = Column(String, nullable=False, default="pending") # "pending", "running", "completed", "failed"
    progress = Column(Float, default=0.0)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    error_message = Column(String, nullable=True)

    source = relationship("KnowledgeSource", back_populates="jobs")
