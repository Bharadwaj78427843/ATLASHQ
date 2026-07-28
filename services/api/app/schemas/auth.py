"""
app/schemas/auth.py

Pydantic v2 schemas for authentication request/response bodies.
"""
from pydantic import BaseModel, EmailStr


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class RegisterRequest(BaseModel):
    """
    Registration payload — mirrors UserCreate but lives in auth schemas
    so the auth router has a self-contained contract.
    Re-uses UserCreate internally.
    """
    email: EmailStr
    username: str
    password: str
    first_name: str | None = None
    last_name: str | None = None
