import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from app.db.base import Base
from app.ai.memory.provider import OrgMemoryProvider
from app.ai.interfaces.memory import MemoryKey, MemoryRecord
import os

TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

@pytest_asyncio.fixture
async def async_session():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    SessionLocal = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    async with SessionLocal() as session:
        yield session
        
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()

@pytest.mark.asyncio
async def test_org_memory_provider(async_session, monkeypatch):
    # Monkeypatch the async_session in provider to use our test session factory
    from app.db import session as db_session
    
    # Simple factory function for tests
    class TestSessionLocal:
        async def __aenter__(self):
            self.session = async_session
            return self.session
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
            
    monkeypatch.setattr(db_session, "async_session", TestSessionLocal)
    
    provider = OrgMemoryProvider()
    key = MemoryKey(scope="organization:test", identifier="run_1")
    record = MemoryRecord(key=key, value={"test_data": "data123"})
    
    # Test Put
    await provider.put(record)
    
    # Test Get
    retrieved = await provider.get(key)
    assert retrieved is not None
    assert retrieved.value == {"test_data": "data123"}
    
    # Test Delete
    await provider.delete(key)
    retrieved_after_del = await provider.get(key)
    assert retrieved_after_del is None
