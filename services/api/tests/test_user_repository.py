"""
tests/test_user_repository.py

Integration tests for UserRepository using an in-memory SQLite database.
No PostgreSQL required — aiosqlite drives the async engine.
"""
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.db.base import Base
from app.models.user import User  # noqa: F401 — register table on Base.metadata
from app.repositories.user import UserRepository
from app.schemas.user import UserCreate, UserUpdate

# ---------------------------------------------------------------------------
# Test database setup — in-memory SQLite, one fresh DB per test function
# ---------------------------------------------------------------------------
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:  # type: ignore[override]
    """Yield an async session backed by a fresh in-memory SQLite database."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(
        bind=engine,
        class_=AsyncSession,
        expire_on_commit=False,
        autoflush=False,
    )
    async with session_factory() as session:
        yield session

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------
def _make_user(
    email: str = "alice@example.com",
    username: str = "alice",
    password: str = "secret1234",
) -> UserCreate:
    return UserCreate(email=email, username=username, password=password)


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
@pytest.mark.asyncio
async def test_create_user(db_session: AsyncSession) -> None:
    """Creating a user returns the persisted User object."""
    repo = UserRepository(db_session)
    user_in = _make_user()
    user = await repo.create_user(user_in)

    assert user.id is not None
    assert user.email == "alice@example.com"
    assert user.username == "alice"
    assert user.password_hash == "secret1234"
    assert user.is_active is True
    assert user.is_verified is False


@pytest.mark.asyncio
async def test_get_user_by_id(db_session: AsyncSession) -> None:
    """get_by_id returns the correct user."""
    repo = UserRepository(db_session)
    created = await repo.create_user(_make_user())

    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id
    assert fetched.email == created.email


@pytest.mark.asyncio
async def test_get_user_by_email(db_session: AsyncSession) -> None:
    """get_by_email returns the correct user."""
    repo = UserRepository(db_session)
    created = await repo.create_user(_make_user())

    fetched = await repo.get_by_email("alice@example.com")
    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_update_user(db_session: AsyncSession) -> None:
    """Updating a user persists the new field values."""
    repo = UserRepository(db_session)
    created = await repo.create_user(_make_user())

    updated = await repo.update_user(
        created.id,
        UserUpdate(first_name="Alice", last_name="Wonderland"),
    )
    assert updated is not None
    assert updated.first_name == "Alice"
    assert updated.last_name == "Wonderland"
    assert updated.email == "alice@example.com"  # unchanged


@pytest.mark.asyncio
async def test_delete_user(db_session: AsyncSession) -> None:
    """Deleting a user returns True and subsequent lookup returns None."""
    repo = UserRepository(db_session)
    created = await repo.create_user(_make_user())

    result = await repo.delete_user(created.id)
    assert result is True

    gone = await repo.get_by_id(created.id)
    assert gone is None


@pytest.mark.asyncio
async def test_duplicate_email_raises(db_session: AsyncSession) -> None:
    """Creating two users with the same email raises ValueError."""
    repo = UserRepository(db_session)
    await repo.create_user(_make_user(email="dup@example.com", username="user1"))

    with pytest.raises(ValueError, match="already exists"):
        await repo.create_user(_make_user(email="dup@example.com", username="user2"))


@pytest.mark.asyncio
async def test_duplicate_username_raises(db_session: AsyncSession) -> None:
    """Creating two users with the same username raises ValueError."""
    repo = UserRepository(db_session)
    await repo.create_user(_make_user(email="a@example.com", username="sameuser"))

    with pytest.raises(ValueError, match="already exists"):
        await repo.create_user(_make_user(email="b@example.com", username="sameuser"))


@pytest.mark.asyncio
async def test_get_missing_user_returns_none(db_session: AsyncSession) -> None:
    """Looking up a non-existent UUID returns None without raising."""
    import uuid
    repo = UserRepository(db_session)

    result = await repo.get_by_id(uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_delete_missing_user_returns_false(db_session: AsyncSession) -> None:
    """Deleting a non-existent user returns False without raising."""
    import uuid
    repo = UserRepository(db_session)

    result = await repo.delete_user(uuid.uuid4())
    assert result is False
