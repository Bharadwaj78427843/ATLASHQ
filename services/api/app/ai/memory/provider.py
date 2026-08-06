"""
app/ai/memory/provider.py

Database-backed memory provider for Organization Memory.
"""
from __future__ import annotations

import json
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete

from app.db.session import async_session
from app.models.memory import DBMemoryRecord
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.interfaces.memory import MemoryKey, MemoryProvider, MemoryRecord


class OrgMemoryProvider(MemoryProvider):
    provider_name = "org_memory"

    def __init__(self, config: dict | None = None) -> None:
        super().__init__(config)

    async def get(self, key: MemoryKey) -> MemoryRecord | None:
        async with async_session() as session:
            stmt = select(DBMemoryRecord).where(
                DBMemoryRecord.scope == key.scope,
                DBMemoryRecord.identifier == key.identifier
            )
            result = await session.execute(stmt)
            record = result.scalar_one_or_none()
            if not record:
                return None
            return MemoryRecord(
                key=key,
                value=record.value,
                metadata=record.metadata_json or {}
            )

    async def put(self, record: MemoryRecord) -> None:
        async with async_session() as session:
            stmt = select(DBMemoryRecord).where(
                DBMemoryRecord.scope == record.key.scope,
                DBMemoryRecord.identifier == record.key.identifier
            )
            result = await session.execute(stmt)
            db_record = result.scalar_one_or_none()
            
            if db_record:
                db_record.value = record.value
                db_record.metadata_json = record.metadata
            else:
                db_record = DBMemoryRecord(
                    scope=record.key.scope,
                    identifier=record.key.identifier,
                    value=record.value,
                    metadata_json=record.metadata
                )
                session.add(db_record)
                
            await session.commit()

    async def delete(self, key: MemoryKey) -> None:
        async with async_session() as session:
            stmt = delete(DBMemoryRecord).where(
                DBMemoryRecord.scope == key.scope,
                DBMemoryRecord.identifier == key.identifier
            )
            await session.execute(stmt)
            await session.commit()

    async def clear(self, scope: str) -> None:
        async with async_session() as session:
            stmt = delete(DBMemoryRecord).where(
                DBMemoryRecord.scope == scope
            )
            await session.execute(stmt)
            await session.commit()

    async def health(self) -> HealthCheckResult:
        try:
            async with async_session() as session:
                await session.execute(select(1))
            return HealthCheckResult(status=HealthStatus.HEALTHY, message="Database memory provider is healthy.")
        except Exception as e:
            return HealthCheckResult(status=HealthStatus.UNHEALTHY, message=f"Database memory provider error: {e}")

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            features=frozenset({"conversation", "workspace", "agent", "long-term", "organization", "project", "execution"})
        )
