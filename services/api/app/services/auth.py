"""
app/services/auth.py

ATLAS-006 / ATLAS-007 — Authentication service layer.

Orchestrates UserRepository, PasswordService, and JWTService.
All business logic lives here; routers stay thin.
"""
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user import UserRepository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead
from app.services.password import PasswordService
from app.services.jwt import JWTService
from app.models.user import User


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self._repo = UserRepository(session)

    # ── Registration ──────────────────────────────────────────────────────────

    async def register(self, payload: RegisterRequest) -> UserRead:
        """
        Hash the password and create the user.
        Raises 409 if email or username is already taken.
        """
        # Check uniqueness before hitting the DB unique constraint
        if await self._repo.get_by_email(payload.email):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Email already registered",
            )
        if await self._repo.get_by_username(payload.username):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username already taken",
            )

        user_in = UserCreate(
            email=payload.email,
            username=payload.username,
            password=PasswordService.hash_password(payload.password),
            first_name=payload.first_name,
            last_name=payload.last_name,
        )
        user: User = await self._repo.create_user(user_in)
        return UserRead.model_validate(user)

    # ── Login ─────────────────────────────────────────────────────────────────

    async def login(self, payload: LoginRequest) -> TokenResponse:
        """
        Verify credentials and return JWT tokens.
        Returns 401 for any invalid credential — no leaking which field failed.
        """
        invalid_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

        user = await self._repo.get_by_email(payload.email)
        if user is None:
            raise invalid_exc

        if not PasswordService.verify_password(payload.password, user.password_hash):
            raise invalid_exc

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is deactivated",
            )

        subject = str(user.id)
        return TokenResponse(
            access_token=JWTService.create_access_token(subject),
            refresh_token=JWTService.create_refresh_token(subject),
        )

    # ── Current user ──────────────────────────────────────────────────────────

    async def get_user_by_id(self, user_id: str) -> User:
        """Fetch a user by string UUID; raises 404 if not found."""
        import uuid
        try:
            uid = uuid.UUID(user_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail="Invalid token subject")
        user = await self._repo.get_by_id(uid)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail="User not found")
        return user
