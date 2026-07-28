"""
tests/test_workspace_api.py

Integration tests for Workspace API and Service logic.
"""
import pytest
import pytest_asyncio
import uuid
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from app.main import app
from app.db.session import get_db
from app.db.base import Base

TEST_DB = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def test_session() -> AsyncSession:  # type: ignore[override]
    engine = create_async_engine(TEST_DB, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
    async with factory() as s:
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest_asyncio.fixture
async def client(test_session: AsyncSession) -> AsyncClient:  # type: ignore[override]
    async def _override():
        yield test_session
    app.dependency_overrides[get_db] = _override
    transport = ASGITransport(app=app) # type: ignore[arg-type]
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()

async def _register(client: AsyncClient, email: str, username: str) -> str:
    await client.post("/auth/register", json={"email": email, "username": username, "password": "Password123!"})
    resp = await client.post("/auth/login", json={"email": email, "password": "Password123!"})
    return resp.json()["access_token"]

def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}

@pytest_asyncio.fixture
async def setup_data(client: AsyncClient) -> dict:
    t_owner = await _register(client, "owner@x.com", "owner")
    t_member = await _register(client, "member@x.com", "member")
    
    # Create Org
    org_resp = await client.post("/api/organizations/", json={"name": "Org", "slug": "org"}, headers=_auth(t_owner))
    org_id = org_resp.json()["id"]
    
    # Owner invites Member, Member accepts
    inv = await client.post(f"/api/organizations/{org_id}/members/invite", json={"email": "member@x.com", "role": "MEMBER"}, headers=_auth(t_owner))
    member_id = inv.json()["id"]
    await client.post(f"/api/organizations/{org_id}/members/{member_id}/accept", headers=_auth(t_member))

    # Owner creates workspace
    ws_resp = await client.post(f"/api/organizations/{org_id}/workspaces/", json={"name": "WS1", "slug": "ws1"}, headers=_auth(t_owner))
    ws_id = ws_resp.json()["id"]
    
    return {
        "t_owner": t_owner,
        "t_member": t_member,
        "org_id": org_id,
        "ws_id": ws_id
    }

@pytest.mark.asyncio
async def test_create_workspace(client: AsyncClient, setup_data: dict):
    # Member cannot create
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/workspaces/", json={"name": "WS2", "slug": "ws2"}, headers=_auth(setup_data["t_member"]))
    assert resp.status_code == 403

    # Owner can create
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/workspaces/", json={"name": "WS2", "slug": "ws2"}, headers=_auth(setup_data["t_owner"]))
    assert resp.status_code == 201
    assert resp.json()["slug"] == "ws2"

@pytest.mark.asyncio
async def test_create_workspace_duplicate_slug(client: AsyncClient, setup_data: dict):
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/workspaces/", json={"name": "WS Dup", "slug": "ws1"}, headers=_auth(setup_data["t_owner"]))
    assert resp.status_code == 409

@pytest.mark.asyncio
async def test_list_workspaces(client: AsyncClient, setup_data: dict):
    resp = await client.get(f"/api/organizations/{setup_data['org_id']}/workspaces/", headers=_auth(setup_data["t_member"]))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] >= 1
    assert any(w["id"] == setup_data["ws_id"] for w in data["items"])

@pytest.mark.asyncio
async def test_get_workspace(client: AsyncClient, setup_data: dict):
    resp = await client.get(f"/api/organizations/{setup_data['org_id']}/workspaces/{setup_data['ws_id']}", headers=_auth(setup_data["t_member"]))
    assert resp.status_code == 200
    assert resp.json()["slug"] == "ws1"

@pytest.mark.asyncio
async def test_update_workspace(client: AsyncClient, setup_data: dict):
    # Member cannot update
    resp = await client.patch(f"/api/organizations/{setup_data['org_id']}/workspaces/{setup_data['ws_id']}", json={"name": "Updated"}, headers=_auth(setup_data["t_member"]))
    assert resp.status_code == 403

    # Owner can update
    resp = await client.patch(f"/api/organizations/{setup_data['org_id']}/workspaces/{setup_data['ws_id']}", json={"name": "Updated"}, headers=_auth(setup_data["t_owner"]))
    assert resp.status_code == 200
    assert resp.json()["name"] == "Updated"

@pytest.mark.asyncio
async def test_delete_workspace(client: AsyncClient, setup_data: dict):
    # Member cannot delete
    resp = await client.delete(f"/api/organizations/{setup_data['org_id']}/workspaces/{setup_data['ws_id']}", headers=_auth(setup_data["t_member"]))
    assert resp.status_code == 403

    # Owner can delete
    resp = await client.delete(f"/api/organizations/{setup_data['org_id']}/workspaces/{setup_data['ws_id']}", headers=_auth(setup_data["t_owner"]))
    assert resp.status_code == 204

    # Verify deleted
    resp = await client.get(f"/api/organizations/{setup_data['org_id']}/workspaces/{setup_data['ws_id']}", headers=_auth(setup_data["t_owner"]))
    assert resp.status_code == 404
