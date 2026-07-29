"""
app/schemas/environment.py

Pydantic models for Environments.
"""
from typing import Optional
from uuid import UUID
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

from app.models.environment import EnvironmentType

class EnvironmentBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=120)
    type: EnvironmentType = Field(default=EnvironmentType.DEVELOPMENT)

class EnvironmentCreate(EnvironmentBase):
    pass

class EnvironmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=120)
    type: Optional[EnvironmentType] = None
    is_active: Optional[bool] = None

class EnvironmentRead(EnvironmentBase):
    id: UUID
    project_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class EnvironmentList(BaseModel):
    items: list[EnvironmentRead]
    total: int
    skip: int
    limit: int
