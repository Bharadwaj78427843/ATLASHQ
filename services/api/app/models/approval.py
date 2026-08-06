"""
app/models/approval.py

Database model for Human Approval Gates.
"""
import uuid as _uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, JSON, Index, DateTime, Boolean
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime, timezone

from app.db.base import Base


class DBApprovalRequest(Base):
    __tablename__ = "approval_requests"

    id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=_uuid.uuid4
    )
    execution_id: Mapped[str] = mapped_column(
        String(255), nullable=False, index=True
    )
    skill_id: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    action: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    risk_level: Mapped[str] = mapped_column(
        String(50), nullable=False
    )
    context_json: Mapped[dict | None] = mapped_column(
        JSON, nullable=True
    )
    requires_reason: Mapped[bool] = mapped_column(
        Boolean, default=False
    )
    timeout_seconds: Mapped[int | None] = mapped_column(
        # We can store an int for timeouts
        nullable=True
    )
    status: Mapped[str] = mapped_column(
        String(50), nullable=False, default="PENDING", index=True
    )
    resolution_reason: Mapped[str | None] = mapped_column(
        String(1000), nullable=True
    )
    resolved_by: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        default=lambda: datetime.now(timezone.utc)
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    __table_args__ = (
        Index("ix_approval_requests_execution_status", "execution_id", "status"),
    )
