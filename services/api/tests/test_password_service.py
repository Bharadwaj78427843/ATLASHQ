"""
tests/test_password_service.py

ATLAS-004 — Unit tests for PasswordService.
No async, no DB — pure unit tests.
"""
import pytest
from app.services.password import PasswordService


def test_hash_is_not_plaintext() -> None:
    """A hash must never equal the plain password."""
    plain = "MySecurePassword123!"
    hashed = PasswordService.hash_password(plain)
    assert hashed != plain


def test_hash_starts_with_argon2_prefix() -> None:
    """Argon2id hashes always start with $argon2id$."""
    hashed = PasswordService.hash_password("hello")
    assert hashed.startswith("$argon2id$")


def test_verify_correct_password_returns_true() -> None:
    """Correct password verifies successfully."""
    plain = "CorrectHorseBatteryStaple"
    hashed = PasswordService.hash_password(plain)
    assert PasswordService.verify_password(plain, hashed) is True


def test_verify_wrong_password_returns_false() -> None:
    """Wrong password returns False without raising."""
    hashed = PasswordService.hash_password("rightpassword")
    assert PasswordService.verify_password("wrongpassword", hashed) is False


def test_verify_empty_string_returns_false() -> None:
    """Empty string should not match a real hash."""
    hashed = PasswordService.hash_password("notblank")
    assert PasswordService.verify_password("", hashed) is False


def test_verify_invalid_hash_returns_false() -> None:
    """Garbage hash string returns False, does not raise."""
    assert PasswordService.verify_password("anypassword", "not_a_valid_hash") is False


def test_two_hashes_of_same_password_differ() -> None:
    """Argon2 uses a random salt — two hashes of the same input must differ."""
    h1 = PasswordService.hash_password("samepassword")
    h2 = PasswordService.hash_password("samepassword")
    assert h1 != h2


def test_needs_rehash_new_hash_is_false() -> None:
    """A freshly-generated hash with current params should not need rehashing."""
    hashed = PasswordService.hash_password("something")
    assert PasswordService.needs_rehash(hashed) is False
