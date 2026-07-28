"""add_organization_members

Revision ID: 0003
Revises: 0002
Create Date: 2026-07-28

Creates the 'organization_members' table and associated ENUMs.
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003"
down_revision: Union[str, None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # We use SQLAlchemy's native Enum type creation which handles Postgres vs SQLite differences automatically.
    role_enum = sa.Enum("OWNER", "ADMIN", "MEMBER", "VIEWER", name="member_role_enum")
    status_enum = sa.Enum("INVITED", "ACTIVE", "SUSPENDED", "LEFT", name="member_status_enum")

    op.create_table(
        "organization_members",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("organization_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("role", role_enum, nullable=False, server_default="MEMBER"),
        sa.Column("status", status_enum, nullable=False, server_default="INVITED"),
        sa.Column("invited_by_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        
        sa.ForeignKeyConstraint(["organization_id"], ["organizations.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["invited_by_id"], ["users.id"], ondelete="SET NULL"),
        sa.UniqueConstraint("organization_id", "user_id", name="uq_organization_user"),
    )
    
    op.create_index("ix_organization_members_org_id", "organization_members", ["organization_id"])
    op.create_index("ix_organization_members_user_id", "organization_members", ["user_id"])
    op.create_index("ix_organization_members_role", "organization_members", ["role"])
    op.create_index("ix_organization_members_status", "organization_members", ["status"])


def downgrade() -> None:
    op.drop_index("ix_organization_members_status", table_name="organization_members")
    op.drop_index("ix_organization_members_role", table_name="organization_members")
    op.drop_index("ix_organization_members_user_id", table_name="organization_members")
    op.drop_index("ix_organization_members_org_id", table_name="organization_members")
    op.drop_table("organization_members")
    
    # We must explicitly drop the enums from Postgres if they exist
    # Use execute to handle the postgres-specific dropping since SQLite doesn't have ENUM types.
    bind = op.get_bind()
    if bind.dialect.name == "postgresql":
        op.execute("DROP TYPE member_role_enum")
        op.execute("DROP TYPE member_status_enum")
