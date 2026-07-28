from pydantic import BaseModel, EmailStr, Field, ConfigDict
from uuid import UUID
from datetime import datetime

class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    first_name: str | None = None
    last_name: str | None = None
    avatar_url: str | None = None
    is_active: bool | None = None
    is_verified: bool | None = None
    password: str | None = Field(None, min_length=8)

class UserRead(UserBase):
    id: UUID
    is_active: bool
    is_verified: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)

class InternalUser(UserRead):
    password_hash: str
