"""
app/models/organization_member.py

OrganizationMember domain model.
Manages RBAC (Role-Based Access Control) and membership lifecycle within an organization.
"""
import uuid as _uuid
from datetime import datetime
import enum

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, DateTime, UniqueConstraint, Enum, Index
from sqlalchemy.dialects.postgresql import UUID

from app.db.base import Base


class MemberRole(str, enum.Enum):
    OWNER = "OWNER"
    ADMIN = "ADMIN"
    MEMBER = "MEMBER"
    VIEWER = "VIEWER"


class MemberStatus(str, enum.Enum):
    INVITED = "INVITED"
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    LEFT = "LEFT"


class OrganizationMember(Base):
    __tablename__ = "organization_members"

    organization_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[_uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    role: Mapped[MemberRole] = mapped_column(
        Enum(MemberRole, name="member_role_enum", create_type=False),
        nullable=False,
        default=MemberRole.MEMBER,
    )

    status: Mapped[MemberStatus] = mapped_column(
        Enum(MemberStatus, name="member_status_enum", create_type=False),
        nullable=False,
        default=MemberStatus.INVITED,
    )

    invited_by_id: Mapped[_uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    joined_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    __table_args__ = (
        UniqueConstraint("organization_id", "user_id", name="uq_organization_user"),
        Index("ix_organization_members_org_id", "organization_id"),
        Index("ix_organization_members_user_id", "user_id"),
        Index("ix_organization_members_role", "role"),
        Index("ix_organization_members_status", "status"),
    )

    # ── Relationships ──────────────────────────────────────────────────────────
    organization = relationship(
        "Organization",
        foreign_keys=[organization_id],
        lazy="noload",
    )
    user = relationship(
        "User",
        foreign_keys=[user_id],
        lazy="noload",
    )
    invited_by = relationship(
        "User",
        foreign_keys=[invited_by_id],
        lazy="noload",
    )
