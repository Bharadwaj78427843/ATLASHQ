"""
scripts/seed_users.py

Inserts three demo users into the database.

Usage (from services/api/):
    uv run python scripts/seed_users.py

Requires DATABASE_URL to point to a running PostgreSQL instance, or falls
back to the default dev URL defined in app/db/session.py.
"""
import sys
import os

# Ensure the services/api directory (parent of scripts/) is on sys.path
# so `app.*` imports resolve correctly when called as a sub-script.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from sqlalchemy.exc import IntegrityError

from app.db.session import async_session
from app.models.user import User  # noqa: F401 — ensure table is registered


DEMO_USERS = [
    {
        "email": "alice@atlashq.com",
        "username": "alice",
        "password_hash": "demo_hash_alice",
        "first_name": "Alice",
        "last_name": "Nguyen",
        "is_active": True,
        "is_verified": True,
    },
    {
        "email": "bob@atlashq.com",
        "username": "bob",
        "password_hash": "demo_hash_bob",
        "first_name": "Bob",
        "last_name": "Smith",
        "is_active": True,
        "is_verified": False,
    },
    {
        "email": "carol@atlashq.com",
        "username": "carol",
        "password_hash": "demo_hash_carol",
        "first_name": "Carol",
        "last_name": "Martinez",
        "is_active": True,
        "is_verified": True,
    },
]


async def seed() -> None:
    async with async_session() as session:
        inserted = 0
        skipped = 0
        for data in DEMO_USERS:
            user = User(**data)
            session.add(user)
            try:
                await session.flush()
                inserted += 1
                print(f"  [OK]   Inserted: {data['email']}")
            except IntegrityError:
                await session.rollback()
                skipped += 1
                print(f"  [SKIP] Already exists: {data['email']}")
                # Re-open a clean transaction for the next user
                async with async_session() as inner_session:
                    pass

        if inserted > 0:
            await session.commit()

    print(f"\nSeed complete — {inserted} inserted, {skipped} skipped.")


if __name__ == "__main__":
    asyncio.run(seed())
