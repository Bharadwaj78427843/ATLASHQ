"""
tests/test_jwt_service.py

ATLAS-005 - Unit tests for JWTService.
Uses real encoding/decoding with a test SECRET_KEY via monkeypatch.
"""
import pytest
from fastapi import HTTPException
from app.services.jwt import JWTService
from app.core.config import get_settings


TEST_SUBJECT = "00000000-0000-0000-0000-000000000001"


def test_create_access_token_returns_string() -> None:
    token = JWTService.create_access_token(TEST_SUBJECT)
    assert isinstance(token, str)
    assert len(token) > 20


def test_create_refresh_token_returns_string() -> None:
    token = JWTService.create_refresh_token(TEST_SUBJECT)
    assert isinstance(token, str)
    assert len(token) > 20


def test_access_token_subject_round_trips() -> None:
    token = JWTService.create_access_token(TEST_SUBJECT)
    subject = JWTService.get_subject(token, expected_type="access")
    assert subject == TEST_SUBJECT


def test_refresh_token_subject_round_trips() -> None:
    token = JWTService.create_refresh_token(TEST_SUBJECT)
    subject = JWTService.get_subject(token, expected_type="refresh")
    assert subject == TEST_SUBJECT


def test_access_token_rejected_as_refresh() -> None:
    """Access token must not be accepted where a refresh token is expected."""
    token = JWTService.create_access_token(TEST_SUBJECT)
    with pytest.raises(HTTPException) as exc_info:
        JWTService.decode_token(token, expected_type="refresh")
    assert exc_info.value.status_code == 401


def test_refresh_token_rejected_as_access() -> None:
    """Refresh token must not be accepted where an access token is expected."""
    token = JWTService.create_refresh_token(TEST_SUBJECT)
    with pytest.raises(HTTPException) as exc_info:
        JWTService.decode_token(token, expected_type="access")
    assert exc_info.value.status_code == 401


def test_tampered_token_raises_401() -> None:
    token = JWTService.create_access_token(TEST_SUBJECT)
    tampered = token[:-4] + "XXXX"
    with pytest.raises(HTTPException) as exc_info:
        JWTService.decode_token(tampered)
    assert exc_info.value.status_code == 401


def test_garbage_token_raises_401() -> None:
    with pytest.raises(HTTPException) as exc_info:
        JWTService.decode_token("not.a.token")
    assert exc_info.value.status_code == 401


def test_expired_token_raises_401() -> None:
    """Forge an already-expired token and confirm it is rejected."""
    from datetime import datetime, timedelta, timezone

    settings = get_settings()
    past = datetime.now(timezone.utc) - timedelta(hours=1)
    payload = {
        "sub": TEST_SUBJECT,
        "type": "access",
        "iat": past,
        "exp": past,
    }
    expired_token = JWTService._encode(payload)

    with pytest.raises(HTTPException) as exc_info:
        JWTService.decode_token(expired_token)
    assert exc_info.value.status_code == 401