from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.memory import DBMemoryRecord

router = APIRouter(prefix="/ai/memory/org", tags=["AI Memory"])

@router.get("/")
async def list_org_memory(session: AsyncSession = Depends(get_db)):
    stmt = select(DBMemoryRecord).where(DBMemoryRecord.scope.like("organization%")).order_by(DBMemoryRecord.updated_at.desc()).limit(100)
    res = await session.execute(stmt)
    records = res.scalars().all()
    return {"records": records}
