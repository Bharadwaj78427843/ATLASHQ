"""
app/ai/skills_runtime/approval.py

Human Approval Gate for intercepting and approving destructive actions.
"""
from __future__ import annotations

import asyncio
from typing import Any
from datetime import datetime, timezone
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import async_session
from app.models.approval import DBApprovalRequest


class ApprovalGate:
    """Manages the creation and resolution of human approval gates."""
    
    async def request_approval(
        self,
        execution_id: str,
        skill_id: str,
        action: str,
        risk_level: str,
        context: dict[str, Any] | None = None,
        requires_reason: bool = False,
        timeout_seconds: int | None = None
    ) -> DBApprovalRequest:
        """Create a new pending approval request and persist it."""
        async with async_session() as session:
            request = DBApprovalRequest(
                execution_id=execution_id,
                skill_id=skill_id,
                action=action,
                risk_level=risk_level,
                context_json=context or {},
                requires_reason=requires_reason,
                timeout_seconds=timeout_seconds,
                status="PENDING"
            )
            session.add(request)
            await session.commit()
            await session.refresh(request)
            return request

    async def wait_for_approval(self, request_id: str, poll_interval: float = 2.0) -> DBApprovalRequest:
        """Poll the database until the request is resolved (APPROVED, REJECTED, TIMED_OUT)."""
        while True:
            async with async_session() as session:
                stmt = select(DBApprovalRequest).where(DBApprovalRequest.id == request_id)
                result = await session.execute(stmt)
                request = result.scalar_one_or_none()
                
                if not request:
                    raise ValueError(f"Approval request {request_id} not found")
                
                if request.status != "PENDING":
                    return request
                    
            await asyncio.sleep(poll_interval)

    async def resolve_approval(
        self, 
        request_id: str, 
        status: str, 
        resolved_by: str, 
        reason: str | None = None
    ) -> DBApprovalRequest:
        """Resolve a pending request."""
        async with async_session() as session:
            stmt = select(DBApprovalRequest).where(DBApprovalRequest.id == request_id)
            result = await session.execute(stmt)
            request = result.scalar_one_or_none()
            
            if not request:
                raise ValueError(f"Approval request {request_id} not found")
                
            if request.status != "PENDING":
                raise ValueError(f"Approval request {request_id} is already {request.status}")
                
            if request.requires_reason and status == "REJECTED" and not reason:
                raise ValueError("A reason is required to reject this request")
                
            request.status = status
            request.resolved_by = resolved_by
            request.resolution_reason = reason
            request.resolved_at = datetime.now(timezone.utc)
            
            await session.commit()
            await session.refresh(request)
            return request
