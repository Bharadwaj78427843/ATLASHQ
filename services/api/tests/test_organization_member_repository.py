"""
tests/test_organization_member_repository.py

Repository-layer tests for OrganizationMemberRepository.
"""
import pytest
import pytest_asyncio
import uuid
from datetime import datetime, timezone

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.models.user import User  # noqa: F401
from app.models.organization import Organization  # noqa: F401
from app.models.organization_member import OrganizationMember, MemberRole, MemberStatus  # noqa: F401
from app.repositories.organization_member import OrganizationMemberRepository
from app.repositories.organization import OrganizationRepository
from app.schemas.organization import OrganizationCreate

TEST_DB = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def session() -> AsyncSession:  # type: ignore[override]
    engine = create_async_engine(TEST_DB, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False, autoflush=False)
    async with factory() as s:
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


async def _seed_user(session: AsyncSession, email: str, username: str) -> User:
    u = User(email=email, username=username, password_hash="x")
    session.add(u)
    await session.commit()
    await session.refresh(u)
    return u


async def _seed_org(session: AsyncSession, owner: User) -> Organization:
    repo = OrganizationRepository(session)
    return await repo.create(OrganizationCreate(name="Acme", slug="acme"), owner_id=owner.id)


@pytest.mark.asyncio
async def test_create_organization_member(session: AsyncSession) -> None:
    owner = await _seed_user(session, "owner@test.com", "owner")
    org = await _seed_org(session, owner)
    
    repo = OrganizationMemberRepository(session)
    member = await repo.create(org.id, owner.id, MemberRole.OWNER, MemberStatus.ACTIVE)
    
    assert member.id is not None
    assert member.role == MemberRole.OWNER
    assert member.status == MemberStatus.ACTIVE
    assert member.user.id == owner.id


@pytest.mark.asyncio
async def test_duplicate_member_raises_integrity_error(session: AsyncSession) -> None:
    u = await _seed_user(session, "u@test.com", "u")
    org = await _seed_org(session, u)
    repo = OrganizationMemberRepository(session)
    await repo.create(org.id, u.id, MemberRole.MEMBER, MemberStatus.INVITED)
    
    with pytest.raises(IntegrityError):
        await repo.create(org.id, u.id, MemberRole.VIEWER, MemberStatus.ACTIVE)


@pytest.mark.asyncio
async def test_get_by_id(session: AsyncSession) -> None:
    u = await _seed_user(session, "u@test.com", "u")
    org = await _seed_org(session, u)
    repo = OrganizationMemberRepository(session)
    m = await repo.create(org.id, u.id, MemberRole.MEMBER, MemberStatus.ACTIVE)
    
    fetched = await repo.get_by_id(m.id)
    assert fetched is not None
    assert fetched.id == m.id


@pytest.mark.asyncio
async def test_get_by_org_and_user(session: AsyncSession) -> None:
    u = await _seed_user(session, "u@test.com", "u")
    org = await _seed_org(session, u)
    repo = OrganizationMemberRepository(session)
    await repo.create(org.id, u.id, MemberRole.MEMBER, MemberStatus.ACTIVE)
    
    fetched = await repo.get_by_org_and_user(org.id, u.id)
    assert fetched is not None


@pytest.mark.asyncio
async def test_exists_returns_true(session: AsyncSession) -> None:
    u = await _seed_user(session, "u@test.com", "u")
    org = await _seed_org(session, u)
    repo = OrganizationMemberRepository(session)
    await repo.create(org.id, u.id, MemberRole.MEMBER, MemberStatus.ACTIVE)
    
    assert await repo.exists(org.id, u.id) is True


@pytest.mark.asyncio
async def test_exists_returns_false_if_missing(session: AsyncSession) -> None:
    u = await _seed_user(session, "u@test.com", "u")
    org = await _seed_org(session, u)
    repo = OrganizationMemberRepository(session)
    
    assert await repo.exists(org.id, u.id) is False


@pytest.mark.asyncio
async def test_soft_delete_hides_member(session: AsyncSession) -> None:
    u = await _seed_user(session, "u@test.com", "u")
    org = await _seed_org(session, u)
    repo = OrganizationMemberRepository(session)
    m = await repo.create(org.id, u.id, MemberRole.MEMBER, MemberStatus.ACTIVE)
    
    await repo.soft_delete(m)
    
    assert await repo.get_by_id(m.id) is None
    assert await repo.get_by_org_and_user(org.id, u.id) is None
    assert await repo.exists(org.id, u.id) is False


@pytest.mark.asyncio
async def test_list_by_organization(session: AsyncSession) -> None:
    u1 = await _seed_user(session, "u1@test.com", "u1")
    u2 = await _seed_user(session, "u2@test.com", "u2")
    org = await _seed_org(session, u1)
    repo = OrganizationMemberRepository(session)
    
    await repo.create(org.id, u1.id, MemberRole.OWNER, MemberStatus.ACTIVE)
    await repo.create(org.id, u2.id, MemberRole.MEMBER, MemberStatus.INVITED)
    
    items, total = await repo.list_by_organization(org.id)
    assert total == 2
    assert len(items) == 2


@pytest.mark.asyncio
async def test_count_owners(session: AsyncSession) -> None:
    u1 = await _seed_user(session, "u1@test.com", "u1")
    u2 = await _seed_user(session, "u2@test.com", "u2")
    org = await _seed_org(session, u1)
    repo = OrganizationMemberRepository(session)
    
    await repo.create(org.id, u1.id, MemberRole.OWNER, MemberStatus.ACTIVE)
    await repo.create(org.id, u2.id, MemberRole.OWNER, MemberStatus.INVITED) # Not active
    
    count = await repo.count_owners(org.id)
    assert count == 1
