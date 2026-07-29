"""
app/models/environment.py

SQLAlchemy model for the Environment domain.
"""
import enum
import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Index, Enum
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

class EnvironmentType(str, enum.Enum):
    DEVELOPMENT = "DEVELOPMENT"
    PREVIEW = "PREVIEW"
    STAGING = "STAGING"
    PRODUCTION = "PRODUCTION"

class Environment(Base):
    __tablename__ = "environments"

    project_id = Column(
        UUID(as_uuid=True),
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    name = Column(String(120), nullable=False)
    type = Column(
        Enum(EnvironmentType, name="environment_type_enum", create_type=False),
        nullable=False,
        default=EnvironmentType.DEVELOPMENT
    )
    is_active = Column(Boolean, default=True, nullable=False)

    __table_args__ = (
        Index("ix_environments_project_id", "project_id"),
    )
