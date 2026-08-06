from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import Any, List
from sqlalchemy import select
from app.db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.approval import DBApprovalRequest

router = APIRouter(prefix="/ai/approvals", tags=["AI Approvals"])

class ApprovalResolveRequest(BaseModel):
    status: str
    reason: str | None = None
    resolved_by: str

@router.get("/")
async def list_approvals(session: AsyncSession = Depends(get_db)):
    stmt = select(DBApprovalRequest).order_by(DBApprovalRequest.created_at.desc()).limit(100)
    res = await session.execute(stmt)
    approvals = res.scalars().all()
    return {"approvals": approvals}

@router.get("/{approval_id}")
async def get_approval(approval_id: str, session: AsyncSession = Depends(get_db)):
    stmt = select(DBApprovalRequest).where(DBApprovalRequest.id == approval_id)
    res = await session.execute(stmt)
    approval = res.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    return approval

@router.post("/{approval_id}/resolve")
async def resolve_approval(approval_id: str, req: ApprovalResolveRequest, session: AsyncSession = Depends(get_db)):
    stmt = select(DBApprovalRequest).where(DBApprovalRequest.id == approval_id)
    res = await session.execute(stmt)
    approval = res.scalar_one_or_none()
    
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    
    if approval.status != "PENDING":
        raise HTTPException(status_code=400, detail="Approval is not PENDING")
        
    approval.status = req.status
    approval.resolution_reason = req.reason
    approval.resolved_by = req.resolved_by
    from datetime import datetime, timezone
    approval.resolved_at = datetime.now(timezone.utc)
    
    await session.commit()
    await session.refresh(approval)
    return approval
