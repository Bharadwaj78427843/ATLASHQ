"""
app/schemas/organization.py

Pydantic v2 schemas for the Organization domain.

Validation rules:
  - slug: lowercase alphanumeric + hyphens, 3–80 chars, no leading/trailing hyphens
  - name: 1–120 chars
  - website: validated URL when provided
  - description: optional, max 1000 chars
"""
import re
from typing import Sequence
from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, Field, field_validator, HttpUrl, ConfigDict, model_validator

_SLUG_RE = re.compile(r"^[a-z0-9]([a-z0-9-]*[a-z0-9])?$")


def _validate_slug(value: str) -> str:
    value = value.strip().lower()
    if not (3 <= len(value) <= 80):
        raise ValueError("Slug must be between 3 and 80 characters")
    if not _SLUG_RE.match(value):
        raise ValueError(
            "Slug may only contain lowercase letters, digits, and hyphens. "
            "It must not start or end with a hyphen."
        )
    return value


class OrganizationCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, description="Display name")
    slug: str = Field(..., description="URL-safe identifier (lowercase, hyphens)")
    description: str | None = Field(None, max_length=1000)
    logo_url: str | None = Field(None, max_length=500)
    website: str | None = Field(None, max_length=500)

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, v: str) -> str:
        return _validate_slug(v)

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        # Basic URL check — must start with http:// or https://
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Website must be a valid URL starting with http:// or https://")
        return v


class OrganizationUpdate(BaseModel):
    """All fields optional for partial update (PATCH semantics)."""
    name: str | None = Field(None, min_length=1, max_length=120)
    description: str | None = Field(None, max_length=1000)
    logo_url: str | None = None
    website: str | None = Field(None, max_length=500)

    @field_validator("website")
    @classmethod
    def validate_website(cls, v: str | None) -> str | None:
        if v is None or v == "":
            return None
        if not (v.startswith("http://") or v.startswith("https://")):
            raise ValueError("Website must be a valid URL starting with http:// or https://")
        return v


class OrganizationRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    slug: str
    description: str | None
    logo_url: str | None
    website: str | None
    owner_id: UUID | None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class OrganizationList(BaseModel):
    """Paginated list response."""
    items: list[OrganizationRead]
    total: int
    skip: int
    limit: int
