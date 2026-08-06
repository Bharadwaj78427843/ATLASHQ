"""
app/models/memory.py

Database model for Organization Memory.
"""
import uuid as _uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, Index, DateTime
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone

from app.db.base import Base


class DBMemoryRecord(Base):
    __tablename__ = "memory_records"

    id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    scope: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    identifier: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    value: Mapped[dict | list | str | int | float | bool | None] = mapped_column(
        JSON, nullable=True
    )
    metadata_json: Mapped[dict | None] = mapped_column(
        JSON, nullable=True, default=dict
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    __table_args__ = (
        Index("ix_memory_records_scope_identifier", "scope", "identifier", unique=True),
    )
