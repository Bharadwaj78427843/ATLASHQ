"""
tests/test_organization_repository.py

Repository-layer tests for OrganizationRepository.
Uses in-memory SQLite — no PostgreSQL required.
"""
import pytest
import pytest_asyncio
import uuid
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.exc import IntegrityError

from app.db.base import Base
from app.models.user import User  # noqa: F401
from app.models.organization import Organization  # noqa: F401
from app.repositories.organization import OrganizationRepository
from app.schemas.organization import OrganizationCreate, OrganizationUpdate

TEST_DB = "sqlite+aiosqlite:///:memory:"


@pytest_asyncio.fixture
async def session() -> AsyncSession:  # type: ignore[override]
    engine = create_async_engine(TEST_DB, connect_args={"check_same_thread": False})
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    factory = async_sessionmaker(bind=engine, class_=AsyncSession,
                                  expire_on_commit=False, autoflush=False)
    async with factory() as s:
        yield s
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


def _make_org_payload(slug: str = "acme-corp", name: str = "Acme Corp") -> OrganizationCreate:
    return OrganizationCreate(name=name, slug=slug)


async def _seed_owner(session: AsyncSession) -> User:
    user = User(
        email="owner@test.com",
        username="owner",
        password_hash="hashed",
    )
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_create_organization(session: AsyncSession) -> None:
    owner = await _seed_owner(session)
    repo = OrganizationRepository(session)
    org = await repo.create(_make_org_payload(), owner_id=owner.id)
    assert org.id is not None
    assert org.slug == "acme-corp"
    assert org.owner_id == owner.id
    assert org.is_active is True


@pytest.mark.asyncio
async def test_get_by_id(session: AsyncSession) -> None:
    owner = await _seed_owner(session)
    repo = OrganizationRepository(session)
    created = await repo.create(_make_org_payload(), owner_id=owner.id)
    fetched = await repo.get_by_id(created.id)
    assert fetched is not None
    assert fetched.id == created.id


@pytest.mark.asyncio
async def test_get_by_slug(session: AsyncSession) -> None:
    owner = await _seed_owner(session)
    repo = OrganizationRepository(session)
    await repo.create(_make_org_payload(slug="my-org"), owner_id=owner.id)
    found = await repo.get_by_slug("my-org")
    assert found is not None
    assert found.slug == "my-org"


@pytest.mark.asyncio
async def test_get_by_id_missing_returns_none(session: AsyncSession) -> None:
    repo = OrganizationRepository(session)
    result = await repo.get_by_id(uuid.uuid4())
    assert result is None


@pytest.mark.asyncio
async def test_get_by_slug_missing_returns_none(session: AsyncSession) -> None:
    repo = OrganizationRepository(session)
    result = await repo.get_by_slug("nonexistent-slug")
    assert result is None


@pytest.mark.asyncio
async def test_exists_slug_true(session: AsyncSession) -> None:
    owner = await _seed_owner(session)
    repo = OrganizationRepository(session)
    await repo.create(_make_org_payload(slug="existing-slug"), owner_id=owner.id)
    assert await repo.exists_slug("existing-slug") is True


@pytest.mark.asyncio
async def test_exists_slug_false(session: AsyncSession) -> None:
    repo = OrganizationRepository(session)
    assert await repo.exists_slug("never-used-slug") is False


@pytest.mark.asyncio
async def test_duplicate_slug_raises_integrity_error(session: AsyncSession) -> None:
    owner = await _seed_owner(session)
    repo = OrganizationRepository(session)
    await repo.create(_make_org_payload(slug="dup-slug"), owner_id=owner.id)
    with pytest.raises(IntegrityError):
        await repo.create(_make_org_payload(slug="dup-slug", name="Other"), owner_id=owner.id)


@pytest.mark.asyncio
async def test_update_organization(session: AsyncSession) -> None:
    owner = await _seed_owner(session)
    repo = OrganizationRepository(session)
    org = await repo.create(_make_org_payload(), owner_id=owner.id)
    updated = await repo.update(org, OrganizationUpdate(name="Updated Name"))
    assert updated.name == "Updated Name"


@pytest.mark.asyncio
async def test_soft_delete(session: AsyncSession) -> None:
    owner = await _seed_owner(session)
    repo = OrganizationRepository(session)
    org = await repo.create(_make_org_payload(), owner_id=owner.id)
    deleted = await repo.soft_delete(org)
    assert deleted.is_active is False


@pytest.mark.asyncio
async def test_list_returns_active_only(session: AsyncSession) -> None:
    owner = await _seed_owner(session)
    repo = OrganizationRepository(session)
    org1 = await repo.create(_make_org_payload(slug="active-org"), owner_id=owner.id)
    org2 = await repo.create(_make_org_payload(slug="inactive-org", name="Inactive"), owner_id=owner.id)
    await repo.soft_delete(org2)
    items, total = await repo.list(active_only=True)
    slugs = [o.slug for o in items]
    assert "active-org" in slugs
    assert "inactive-org" not in slugs
    assert total == 1


@pytest.mark.asyncio
async def test_list_by_owner(session: AsyncSession) -> None:
    owner = await _seed_owner(session)
    other = User(email="other@test.com", username="other", password_hash="x")
    session.add(other)
    await session.commit()
    await session.refresh(other)

    repo = OrganizationRepository(session)
    await repo.create(_make_org_payload(slug="owner-org"), owner_id=owner.id)
    await repo.create(_make_org_payload(slug="other-org", name="Other"), owner_id=other.id)

    items, total = await repo.list_by_owner(owner_id=owner.id)
    assert total == 1
    assert items[0].slug == "owner-org"
