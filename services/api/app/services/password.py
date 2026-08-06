"""
app/services/password.py

ATLAS-004 - Password hashing service using Argon2.

Argon2 is the winner of the Password Hashing Competition and is the
recommended algorithm for new applications (superior to bcrypt/scrypt).
When Argon2 is unavailable in the active environment, the service falls
back to PBKDF2 so the API can still boot and tests can run.
"""
from __future__ import annotations

import base64
import hashlib
from hmac import compare_digest
import secrets

try:  # pragma: no cover - exercised when argon2 is installed
    from argon2 import PasswordHasher
    from argon2.exceptions import InvalidHashError, VerificationError, VerifyMismatchError
except ModuleNotFoundError:  # pragma: no cover - exercised in stripped test envs
    PasswordHasher = None
    InvalidHashError = PasswordHasherError = VerificationError = VerifyMismatchError = Exception  # type: ignore[assignment]


_ph = PasswordHasher(
    time_cost=2,
    memory_cost=65536,
    parallelism=2,
    hash_len=32,
    salt_len=16,
) if PasswordHasher is not None else None

_PBKDF2_ITERATIONS = 210_000


def _pbkdf2_hash(plain: str) -> str:
    salt = secrets.token_bytes(16)
    derived = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt, _PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        _PBKDF2_ITERATIONS,
        base64.b64encode(salt).decode("ascii"),
        base64.b64encode(derived).decode("ascii"),
    )


def _pbkdf2_verify(plain: str, hashed: str) -> bool:
    try:
        _, iterations_text, salt_text, hash_text = hashed.split("$", 3)
        iterations = int(iterations_text)
        salt = base64.b64decode(salt_text.encode("ascii"))
        expected = base64.b64decode(hash_text.encode("ascii"))
    except Exception:
        return False

    derived = hashlib.pbkdf2_hmac("sha256", plain.encode("utf-8"), salt, iterations)
    return compare_digest(derived, expected)


class PasswordService:
    """Stateless service for hashing and verifying passwords."""

    @staticmethod
    def hash_password(plain: str) -> str:
        if _ph is not None:
            return _ph.hash(plain)
        return _pbkdf2_hash(plain)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """Return True if *plain* matches *hashed*, False otherwise."""
        try:
            if _ph is not None and not hashed.startswith("pbkdf2_sha256$"):
                return _ph.verify(hashed, plain)
            return _pbkdf2_verify(plain, hashed)
        except (VerifyMismatchError, VerificationError, InvalidHashError, ValueError):
            return False

    @staticmethod
    def needs_rehash(hashed: str) -> bool:
        if _ph is None:
            return False
        if hashed.startswith("pbkdf2_sha256$"):
            return True
        return _ph.check_needs_rehash(hashed)