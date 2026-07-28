"""
app/models/organization.py

Organization domain model — the multi-tenancy root for Atlas.
Every workspace, project, and AI resource belongs to an organization.

Cascade behavior:
  - owner_id FK: SET NULL on user delete (org survives, becomes ownerless)
    This is a deliberate decision: deleting a user must not cascade-delete
    entire organizational structures. An admin workflow must handle
    ownership transfer or org cleanup separately.
  - Soft delete is implemented via is_active=False; hard deletes are
    never performed through the API layer.
"""
import uuid as _uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class Organization(Base):
    __tablename__ = "organizations"

    # ── Core identity ──────────────────────────────────────────────────────────
    name: Mapped[str] = mapped_column(
        String(120),
        nullable=False,
        index=True,
    )
    slug: Mapped[str] = mapped_column(
        String(80),
        nullable=False,
        unique=True,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    logo_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # ── Ownership ──────────────────────────────────────────────────────────────
    owner_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,      # nullable so org survives user deletion
        index=True,
    )

    # ── Status ─────────────────────────────────────────────────────────────────
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )

    # ── Relationships (lazy="noload" — explicitly loaded when needed) ──────────
    owner = relationship(
        "User",
        foreign_keys=[owner_id],
        lazy="noload",
    )
