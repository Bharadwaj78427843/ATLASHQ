"""
app/schemas/organization_member.py

Pydantic schemas for Organization Membership domain.
"""
from typing import Sequence
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, EmailStr, ConfigDict

from app.models.organization_member import MemberRole, MemberStatus
from app.schemas.user import UserRead


class InviteMemberRequest(BaseModel):
    """Payload for POST /invite"""
    email: EmailStr
    role: MemberRole = Field(default=MemberRole.MEMBER)


class UpdateMemberRole(BaseModel):
    """Payload for PATCH /{member_id}"""
    role: MemberRole


class TransferOwnershipRequest(BaseModel):
    """Payload for POST /transfer-owner"""
    target_user_id: UUID


class OrganizationMemberRead(BaseModel):
    """Read schema. Includes nested user for display."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    organization_id: UUID
    user_id: UUID
    role: MemberRole
    status: MemberStatus
    invited_by_id: UUID | None
    joined_at: datetime | None
    created_at: datetime
    updated_at: datetime

    # The relationship to the user should be included for the frontend
    user: UserRead


class OrganizationMemberList(BaseModel):
    """Paginated list response."""
    items: list[OrganizationMemberRead]
    total: int
    skip: int
    limit: int
