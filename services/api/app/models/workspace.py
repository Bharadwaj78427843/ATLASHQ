"""
app/models/workspace.py

Workspace domain model.
A workspace belongs to an Organization and houses Projects.
"""
import uuid as _uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base

class Workspace(Base):
    __tablename__ = "workspaces"

    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    organization_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("organization_id", "slug", name="uq_workspace_org_slug"),
        Index("ix_workspaces_org_id", "organization_id"),
        Index("ix_workspaces_slug", "slug"),
        Index("ix_workspaces_is_active", "is_active"),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    organization = relationship(
        "Organization",
        foreign_keys=[organization_id],
        lazy="noload",
    )
