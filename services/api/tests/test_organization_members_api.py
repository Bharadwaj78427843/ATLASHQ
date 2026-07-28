"""
tests/test_organization_members_api.py

Integration tests for Organization Membership API and Service logic.
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
    t_admin = await _register(client, "admin@x.com", "admin")
    t_member = await _register(client, "member@x.com", "member")
    t_target = await _register(client, "target@x.com", "target")
    
    # Create Org
    org_resp = await client.post("/api/organizations/", json={"name": "Org", "slug": "org"}, headers=_auth(t_owner))
    org_id = org_resp.json()["id"]
    
    # Owner invites Admin
    inv_admin = await client.post(f"/api/organizations/{org_id}/members/invite", json={"email": "admin@x.com", "role": "ADMIN"}, headers=_auth(t_owner))
    await client.post(f"/api/organizations/{org_id}/members/{inv_admin.json()['id']}/accept", headers=_auth(t_admin))
    
    # Owner invites Member
    inv_mem = await client.post(f"/api/organizations/{org_id}/members/invite", json={"email": "member@x.com", "role": "MEMBER"}, headers=_auth(t_owner))
    await client.post(f"/api/organizations/{org_id}/members/{inv_mem.json()['id']}/accept", headers=_auth(t_member))
    
    return {
        "org_id": org_id,
        "t_owner": t_owner, "t_admin": t_admin, "t_member": t_member, "t_target": t_target,
        "target_email": "target@x.com"
    }

# ── Invite ────────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_invite_member_success(client: AsyncClient, setup_data: dict) -> None:
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/members/invite", 
                             json={"email": setup_data["target_email"], "role": "VIEWER"}, 
                             headers=_auth(setup_data["t_admin"]))
    assert resp.status_code == 201
    assert resp.json()["role"] == "VIEWER"
    assert resp.json()["status"] == "INVITED"
    assert resp.json()["user"]["email"] == setup_data["target_email"]

@pytest.mark.asyncio
async def test_invite_member_requires_auth(client: AsyncClient, setup_data: dict) -> None:
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/members/invite", 
                             json={"email": setup_data["target_email"], "role": "VIEWER"})
    assert resp.status_code == 401

@pytest.mark.asyncio
async def test_invite_member_requires_admin_or_owner(client: AsyncClient, setup_data: dict) -> None:
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/members/invite", 
                             json={"email": setup_data["target_email"], "role": "VIEWER"}, 
                             headers=_auth(setup_data["t_member"])) # Normal member
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_invite_member_admin_cannot_invite_owner(client: AsyncClient, setup_data: dict) -> None:
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/members/invite", 
                             json={"email": setup_data["target_email"], "role": "OWNER"}, 
                             headers=_auth(setup_data["t_admin"]))
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_invite_member_owner_can_invite_owner(client: AsyncClient, setup_data: dict) -> None:
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/members/invite", 
                             json={"email": setup_data["target_email"], "role": "OWNER"}, 
                             headers=_auth(setup_data["t_owner"]))
    assert resp.status_code == 201

@pytest.mark.asyncio
async def test_invite_duplicate_returns_409(client: AsyncClient, setup_data: dict) -> None:
    await client.post(f"/api/organizations/{setup_data['org_id']}/members/invite", 
                      json={"email": setup_data["target_email"], "role": "MEMBER"}, 
                      headers=_auth(setup_data["t_admin"]))
    
    resp2 = await client.post(f"/api/organizations/{setup_data['org_id']}/members/invite", 
                              json={"email": setup_data["target_email"], "role": "MEMBER"}, 
                              headers=_auth(setup_data["t_admin"]))
    assert resp2.status_code == 409

@pytest.mark.asyncio
async def test_invite_unknown_user_returns_404(client: AsyncClient, setup_data: dict) -> None:
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/members/invite", 
                             json={"email": "nobody@x.com", "role": "MEMBER"}, 
                             headers=_auth(setup_data["t_admin"]))
    assert resp.status_code == 404

# ── Accept / Reject ───────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_accept_invitation(client: AsyncClient, setup_data: dict) -> None:
    inv = await client.post(f"/api/organizations/{setup_data['org_id']}/members/invite", 
                            json={"email": setup_data["target_email"], "role": "MEMBER"}, 
                            headers=_auth(setup_data["t_owner"]))
    inv_id = inv.json()["id"]
    
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/members/{inv_id}/accept", 
                             headers=_auth(setup_data["t_target"]))
    assert resp.status_code == 200
    assert resp.json()["status"] == "ACTIVE"

@pytest.mark.asyncio
async def test_accept_invitation_wrong_user_returns_403(client: AsyncClient, setup_data: dict) -> None:
    inv = await client.post(f"/api/organizations/{setup_data['org_id']}/members/invite", 
                            json={"email": setup_data["target_email"], "role": "MEMBER"}, 
                            headers=_auth(setup_data["t_owner"]))
    inv_id = inv.json()["id"]
    
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/members/{inv_id}/accept", 
                             headers=_auth(setup_data["t_member"]))
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_reject_invitation(client: AsyncClient, setup_data: dict) -> None:
    inv = await client.post(f"/api/organizations/{setup_data['org_id']}/members/invite", 
                            json={"email": setup_data["target_email"], "role": "MEMBER"}, 
                            headers=_auth(setup_data["t_owner"]))
    inv_id = inv.json()["id"]
    
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/members/{inv_id}/reject", 
                             headers=_auth(setup_data["t_target"]))
    assert resp.status_code == 204
    
    # Verify soft deleted
    list_resp = await client.get(f"/api/organizations/{setup_data['org_id']}/members/", headers=_auth(setup_data["t_owner"]))
    ids = [m["id"] for m in list_resp.json()["items"]]
    assert inv_id not in ids

# ── List & Get ────────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_list_members(client: AsyncClient, setup_data: dict) -> None:
    resp = await client.get(f"/api/organizations/{setup_data['org_id']}/members/", headers=_auth(setup_data["t_member"]))
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 3 # owner, admin, member
    roles = [m["role"] for m in data["items"]]
    assert "OWNER" in roles
    assert "ADMIN" in roles
    assert "MEMBER" in roles

@pytest.mark.asyncio
async def test_list_members_outsider_returns_403(client: AsyncClient, setup_data: dict) -> None:
    resp = await client.get(f"/api/organizations/{setup_data['org_id']}/members/", headers=_auth(setup_data["t_target"]))
    assert resp.status_code == 403

# ── Update Role ───────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_update_role_success(client: AsyncClient, setup_data: dict) -> None:
    # get member's id
    list_resp = await client.get(f"/api/organizations/{setup_data['org_id']}/members/", headers=_auth(setup_data["t_owner"]))
    member_id = next(m["id"] for m in list_resp.json()["items"] if m["role"] == "MEMBER")
    
    resp = await client.patch(f"/api/organizations/{setup_data['org_id']}/members/{member_id}", 
                              json={"role": "VIEWER"}, headers=_auth(setup_data["t_admin"]))
    assert resp.status_code == 200
    assert resp.json()["role"] == "VIEWER"

@pytest.mark.asyncio
async def test_update_role_admin_cannot_update_owner(client: AsyncClient, setup_data: dict) -> None:
    list_resp = await client.get(f"/api/organizations/{setup_data['org_id']}/members/", headers=_auth(setup_data["t_owner"]))
    owner_id = next(m["id"] for m in list_resp.json()["items"] if m["role"] == "OWNER")
    
    resp = await client.patch(f"/api/organizations/{setup_data['org_id']}/members/{owner_id}", 
                              json={"role": "MEMBER"}, headers=_auth(setup_data["t_admin"]))
    assert resp.status_code == 403

@pytest.mark.asyncio
async def test_update_role_cannot_downgrade_last_owner(client: AsyncClient, setup_data: dict) -> None:
    list_resp = await client.get(f"/api/organizations/{setup_data['org_id']}/members/", headers=_auth(setup_data["t_owner"]))
    owner_id = next(m["id"] for m in list_resp.json()["items"] if m["role"] == "OWNER")
    
    resp = await client.patch(f"/api/organizations/{setup_data['org_id']}/members/{owner_id}", 
                              json={"role": "ADMIN"}, headers=_auth(setup_data["t_owner"]))
    assert resp.status_code == 400

# ── Transfer Ownership ────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_transfer_ownership_success(client: AsyncClient, setup_data: dict) -> None:
    list_resp = await client.get(f"/api/organizations/{setup_data['org_id']}/members/", headers=_auth(setup_data["t_owner"]))
    admin_m = next(m for m in list_resp.json()["items"] if m["role"] == "ADMIN")
    
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/members/transfer-owner", 
                             json={"target_user_id": admin_m["user"]["id"]}, headers=_auth(setup_data["t_owner"]))
    assert resp.status_code == 204
    
    # Verify new owner
    list_resp2 = await client.get(f"/api/organizations/{setup_data['org_id']}/members/", headers=_auth(setup_data["t_admin"]))
    new_owner = next(m for m in list_resp2.json()["items"] if m["user"]["id"] == admin_m["user"]["id"])
    assert new_owner["role"] == "OWNER"

@pytest.mark.asyncio
async def test_transfer_ownership_requires_owner(client: AsyncClient, setup_data: dict) -> None:
    list_resp = await client.get(f"/api/organizations/{setup_data['org_id']}/members/", headers=_auth(setup_data["t_owner"]))
    member_u = next(m for m in list_resp.json()["items"] if m["role"] == "MEMBER")
    
    resp = await client.post(f"/api/organizations/{setup_data['org_id']}/members/transfer-owner", 
                             json={"target_user_id": member_u["user"]["id"]}, headers=_auth(setup_data["t_admin"]))
    assert resp.status_code == 403

# ── Remove Member ─────────────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_remove_member_success(client: AsyncClient, setup_data: dict) -> None:
    list_resp = await client.get(f"/api/organizations/{setup_data['org_id']}/members/", headers=_auth(setup_data["t_owner"]))
    member_id = next(m["id"] for m in list_resp.json()["items"] if m["role"] == "MEMBER")
    
    resp = await client.delete(f"/api/organizations/{setup_data['org_id']}/members/{member_id}", headers=_auth(setup_data["t_admin"]))
    assert resp.status_code == 204

@pytest.mark.asyncio
async def test_remove_member_self_leave(client: AsyncClient, setup_data: dict) -> None:
    list_resp = await client.get(f"/api/organizations/{setup_data['org_id']}/members/", headers=_auth(setup_data["t_owner"]))
    member_id = next(m["id"] for m in list_resp.json()["items"] if m["role"] == "MEMBER")
    
    resp = await client.delete(f"/api/organizations/{setup_data['org_id']}/members/{member_id}", headers=_auth(setup_data["t_member"]))
    assert resp.status_code == 204
    
    # Should be status=LEFT now
    # ... Wait, if they left they can't fetch it anymore.

@pytest.mark.asyncio
async def test_remove_member_last_owner_fails(client: AsyncClient, setup_data: dict) -> None:
    list_resp = await client.get(f"/api/organizations/{setup_data['org_id']}/members/", headers=_auth(setup_data["t_owner"]))
    owner_id = next(m["id"] for m in list_resp.json()["items"] if m["role"] == "OWNER")
    
    resp = await client.delete(f"/api/organizations/{setup_data['org_id']}/members/{owner_id}", headers=_auth(setup_data["t_owner"]))
    assert resp.status_code == 400
