import pytest
from app.ai.skills_runtime.approval import ApprovalGate
from app.models.memory import DBMemoryRecord
import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_approval_gate_request():
    gate = ApprovalGate()
    
    # Mocking DB insertion
    gate.request_approval = AsyncMock()
    class RequestMock:
        id = uuid.uuid4()
    gate.request_approval.return_value = RequestMock()
    
    req = await gate.request_approval(
        execution_id="exec_1",
        skill_id="orchestrator",
        action="retry_failed_node",
        risk_level="high",
        requires_reason=True
    )
    
    assert req.id is not None

@pytest.mark.asyncio
async def test_approval_gate_wait():
    gate = ApprovalGate()
    
    class WaitMock:
        status = "APPROVED"
        resolved_by = "test_user"
        resolution_reason = "looks good"
        
    gate.wait_for_approval = AsyncMock(return_value=WaitMock())
    
    res = await gate.wait_for_approval("some_id")
    assert res.status == "APPROVED"
    assert res.resolved_by == "test_user"
