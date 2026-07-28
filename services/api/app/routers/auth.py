"""
app/routers/auth.py

ATLAS-006 / ATLAS-007 / ATLAS-008 — Authentication endpoints.

POST /auth/register — create account
POST /auth/login    — get tokens
GET  /auth/me       — get current authenticated user
"""
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserRead
from app.services.auth import AuthService
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter(prefix="/auth", tags=["auth"])


# ── ATLAS-006: Registration ────────────────────────────────────────────────────

@router.post(
    "/register",
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account",
)
async def register(
    payload: RegisterRequest,
    session: AsyncSession = Depends(get_db),
) -> UserRead:
    return await AuthService(session).register(payload)


# ── ATLAS-007: Login ───────────────────────────────────────────────────────────

@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Authenticate and receive JWT tokens",
)
async def login(
    payload: LoginRequest,
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    return await AuthService(session).login(payload)


# ── ATLAS-008: Protected current-user endpoint ────────────────────────────────

@router.get(
    "/me",
    response_model=UserRead,
    summary="Get the currently authenticated user",
)
async def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return UserRead.model_validate(current_user)
