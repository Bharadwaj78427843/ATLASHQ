"""
app/services/password.py

ATLAS-004 — Password hashing service using Argon2.

Argon2 is the winner of the Password Hashing Competition and is the
recommended algorithm for new applications (superior to bcrypt/scrypt).
"""
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError, VerificationError, InvalidHashError

# One shared PasswordHasher instance — it is thread-safe and stateless.
_ph = PasswordHasher(
    time_cost=2,        # iterations (OWASP minimum is 1, 2 gives margin)
    memory_cost=65536,  # 64 MiB
    parallelism=2,      # threads
    hash_len=32,
    salt_len=16,
)


class PasswordService:
    """Stateless service for hashing and verifying passwords with Argon2id."""

    @staticmethod
    def hash_password(plain: str) -> str:
        """Return an Argon2id hash of *plain*."""
        return _ph.hash(plain)

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        """
        Return True if *plain* matches *hashed*, False otherwise.
        Never raises — caller-friendly boolean contract.
        """
        try:
            return _ph.verify(hashed, plain)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False

    @staticmethod
    def needs_rehash(hashed: str) -> bool:
        """Return True if the hash was produced with outdated parameters."""
        return _ph.check_needs_rehash(hashed)
