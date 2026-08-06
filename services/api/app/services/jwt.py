"""
app/services/jwt.py

ATLAS-005 - JWT access and refresh token service.

Uses HS256 signing. Configuration is read from app.core.config.Settings.
Token type is embedded in the payload (`type` claim) to prevent
access tokens from being used where refresh tokens are expected.
When python-jose is unavailable, the service falls back to a small
stdlib HS256 implementation so the API can still boot in minimal envs.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import json
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status

from app.core.config import get_settings

try:  # pragma: no cover - exercised when python-jose is installed
    from jose import JWTError, jwt
except ModuleNotFoundError:  # pragma: no cover - exercised in stripped test envs
    JWTError = Exception  # type: ignore[assignment]
    jwt = None


def _b64url_encode(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode("ascii")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode((value + padding).encode("ascii"))


def _coerce_datetime(value: Any) -> Any:
    if isinstance(value, datetime):
        return int(value.timestamp())
    return value


class JWTService:
    """Stateless JWT factory and validator."""

    @staticmethod
    def _encode(payload: dict[str, Any]) -> str:
        settings = get_settings()
        if jwt is not None:
            return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

        header = {"alg": settings.ALGORITHM, "typ": "JWT"}
        normalized = {key: _coerce_datetime(value) for key, value in payload.items()}
        header_bytes = json.dumps(header, separators=(",", ":"), sort_keys=True).encode("utf-8")
        payload_bytes = json.dumps(normalized, separators=(",", ":"), sort_keys=True).encode("utf-8")
        signing_input = f"{_b64url_encode(header_bytes)}.{_b64url_encode(payload_bytes)}".encode("ascii")
        signature = hmac.new(settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256).digest()
        return f"{signing_input.decode('ascii')}.{_b64url_encode(signature)}"

    @staticmethod
    def create_access_token(subject: str) -> str:
        """Create a short-lived access token."""
        settings = get_settings()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        payload = {"sub": subject, "type": "access", "iat": now, "exp": expire}
        return JWTService._encode(payload)

    @staticmethod
    def create_refresh_token(subject: str) -> str:
        """Create a long-lived refresh token."""
        settings = get_settings()
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        payload = {"sub": subject, "type": "refresh", "iat": now, "exp": expire}
        return JWTService._encode(payload)

    @staticmethod
    def _decode_fallback(token: str) -> dict[str, Any]:
        settings = get_settings()
        try:
            header_b64, payload_b64, signature_b64 = token.split(".", 2)
        except ValueError as exc:
            raise JWTError("Malformed token") from exc

        signing_input = f"{header_b64}.{payload_b64}".encode("ascii")
        expected_signature = hmac.new(
            settings.SECRET_KEY.encode("utf-8"), signing_input, hashlib.sha256
        ).digest()
        actual_signature = _b64url_decode(signature_b64)
        if not hmac.compare_digest(expected_signature, actual_signature):
            raise JWTError("Signature mismatch")

        try:
            payload = json.loads(_b64url_decode(payload_b64).decode("utf-8"))
        except Exception as exc:  # noqa: BLE001
            raise JWTError("Invalid payload") from exc

        exp = payload.get("exp")
        if isinstance(exp, (int, float)):
            if datetime.now(timezone.utc).timestamp() >= float(exp):
                raise JWTError("Token expired")
        elif isinstance(exp, str):
            try:
                if datetime.now(timezone.utc) >= datetime.fromisoformat(exp):
                    raise JWTError("Token expired")
            except ValueError as exc:
                raise JWTError("Invalid exp claim") from exc
        else:
            raise JWTError("Missing exp claim")

        return payload

    @staticmethod
    def decode_token(token: str, expected_type: str = "access") -> dict[str, Any]:
        """Decode and validate a JWT."""
        credentials_exc = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            if jwt is not None:
                settings = get_settings()
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            else:
                payload = JWTService._decode_fallback(token)
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
        """Convenience wrapper - returns just the `sub` claim."""
        return JWTService.decode_token(token, expected_type)["sub"]