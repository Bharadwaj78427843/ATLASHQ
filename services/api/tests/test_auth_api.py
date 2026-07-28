"""
tests/test_auth_api.py

ATLAS-006 / ATLAS-007 / ATLAS-008 — Integration tests for auth endpoints.

Uses httpx.AsyncClient against the FastAPI app with an in-memory SQLite DB.
No live PostgreSQL required.
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.session import get_db
from app.db.base import Base
from app.models.user import User  # noqa: F401 — register table

# ── In-memory SQLite test database ────────────────────────────────────────────
TEST_DB_URL = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def test_session() -> AsyncSession:  # type: ignore[override]
    engine = create_async_engine(TEST_DB_URL, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(bind=engine, class_=AsyncSession,
                                  expire_on_commit=False, autoflush=False)
    async with factory() as session:
        yield session
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest_asyncio.fixture
async def client(test_session: AsyncSession) -> AsyncClient:  # type: ignore[override]
    """AsyncClient with the DB dependency overridden to use SQLite."""
    async def _override_get_db():
        yield test_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)  # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


# ── Helpers ───────────────────────────────────────────────────────────────────

REGISTER_PAYLOAD = {
    "email": "testuser@example.com",
    "username": "testuser",
    "password": "SecurePass123!",
    "first_name": "Test",
    "last_name": "User",
}


async def _register_and_login(client: AsyncClient) -> dict:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    resp = await client.post("/auth/login", json={
        "email": REGISTER_PAYLOAD["email"],
        "password": REGISTER_PAYLOAD["password"],
    })
    return resp.json()


# ── ATLAS-006: Registration tests ─────────────────────────────────────────────

@pytest.mark.asyncio
async def test_register_success(client: AsyncClient) -> None:
    resp = await client.post("/auth/register", json=REGISTER_PAYLOAD)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == REGISTER_PAYLOAD["email"]
    assert data["username"] == REGISTER_PAYLOAD["username"]
    assert "password_hash" not in data  # never leak hash
    assert "id" in data


@pytest.mark.asyncio
async def test_register_duplicate_email_returns_409(client: AsyncClient) -> None:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    resp = await client.post("/auth/register", json={
        **REGISTER_PAYLOAD,
        "username": "other_username",
    })
    assert resp.status_code == 409
    assert "Email" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_register_duplicate_username_returns_409(client: AsyncClient) -> None:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    resp = await client.post("/auth/register", json={
        **REGISTER_PAYLOAD,
        "email": "another@example.com",
    })
    assert resp.status_code == 409
    assert "Username" in resp.json()["detail"]


@pytest.mark.asyncio
async def test_register_invalid_email_returns_422(client: AsyncClient) -> None:
    resp = await client.post("/auth/register", json={
        **REGISTER_PAYLOAD,
        "email": "not-an-email",
    })
    assert resp.status_code == 422


# ── ATLAS-007: Login tests ─────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_login_success_returns_tokens(client: AsyncClient) -> None:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    resp = await client.post("/auth/login", json={
        "email": REGISTER_PAYLOAD["email"],
        "password": REGISTER_PAYLOAD["password"],
    })
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert "refresh_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password_returns_401(client: AsyncClient) -> None:
    await client.post("/auth/register", json=REGISTER_PAYLOAD)
    resp = await client.post("/auth/login", json={
        "email": REGISTER_PAYLOAD["email"],
        "password": "WrongPassword!",
    })
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_login_unknown_email_returns_401(client: AsyncClient) -> None:
    resp = await client.post("/auth/login", json={
        "email": "nobody@example.com",
        "password": "anypassword",
    })
    assert resp.status_code == 401


# ── ATLAS-008: Protected route tests ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_me_returns_current_user(client: AsyncClient) -> None:
    tokens = await _register_and_login(client)
    resp = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == REGISTER_PAYLOAD["email"]


@pytest.mark.asyncio
async def test_me_without_token_returns_401(client: AsyncClient) -> None:
    resp = await client.get("/auth/me")
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_invalid_token_returns_401(client: AsyncClient) -> None:
    resp = await client.get(
        "/auth/me",
        headers={"Authorization": "Bearer this.is.garbage"},
    )
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_me_with_refresh_token_rejected(client: AsyncClient) -> None:
    """Refresh tokens must NOT be accepted on protected access-token endpoints."""
    tokens = await _register_and_login(client)
    resp = await client.get(
        "/auth/me",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )
    assert resp.status_code == 401
