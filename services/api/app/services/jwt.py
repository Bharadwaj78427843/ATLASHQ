"""
app/services/jwt.py

ATLAS-005 — JWT access and refresh token service.

Uses HS256 signing. Configuration is read from app.core.config.Settings.
Token type is embedded in the payload (`type` claim) to prevent
access tokens being used where refresh tokens are expected.
"""
from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from fastapi import HTTPException, status

from app.core.config import get_settings


class JWTService:
    """Stateless JWT factory and validator."""

    # ── Token creation ────────────────────────────────────────────────────────

    @staticmethod
    def _encode(payload: dict[str, Any]) -> str:
        settings = get_settings()
        return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    @staticmethod
    def create_access_token(subject: str) -> str:
        """
        Create a short-lived access token.

        *subject* is the user's string UUID.
        """
        settings = get_settings()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {
            "sub": subject,
            "type": "access",
            "iat": now,
            "exp": expire,
        }
        return JWTService._encode(payload)

    @staticmethod
    def create_refresh_token(subject: str) -> str:
        """Create a long-lived refresh token."""
        settings = get_settings()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {
            "sub": subject,
            "type": "refresh",
            "iat": now,
            "exp": expire,
        }
        return JWTService._encode(payload)

    # ── Token validation ──────────────────────────────────────────────────────

    @staticmethod
    def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
        """
        Decode and validate a JWT.

        Raises HTTPException 401 for any invalid / expired token.
        Returns the full decoded payload on success.
        """
        settings = get_settings()
        credentials_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
            )
        except JWTError:
            raise credentials_exc

        token_type: str | None = payload.get("type")
        if token_type != expected_type:
            raise credentials_exc

        subject: str | None = payload.get("sub")
        if subject is None:
            raise credentials_exc

        return payload

    @staticmethod
    def get_subject(token: str, expected_type: str = "access") -> str:
        """Convenience wrapper — returns just the `sub` claim."""
        return JWTService.decode_token(token, expected_type)["sub"]
