"""
app/dependencies.py

ATLAS-008 — FastAPI dependency injection.

get_current_user extracts and validates the Bearer JWT from the
Authorization header and returns the corresponding User model.
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.services.jwt import JWTService
from app.services.auth import AuthService
from app.models.user import User

# HTTPBearer does NOT auto-error on missing header (auto_error=False)
# so we can return a clean 401 instead of FastAPI's default 403.
_bearer = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
    session: AsyncSession = Depends(get_db),
) -> User:
    """
    Validate Bearer JWT and return the authenticated User.
    Raises 401 for missing, invalid, or expired tokens.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = credentials.credentials
    subject = JWTService.get_subject(token, expected_type="access")

    auth_service = AuthService(session)
    return await auth_service.get_user_by_id(subject)
