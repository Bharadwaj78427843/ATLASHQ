from app.ai.skills_runtime.approval import ApprovalGate

class ApprovalsPipeline:
    def __init__(self, approval_gate: ApprovalGate):
        self._approval_gate = approval_gate

    async def resolve(self, request_id: str, status: str, resolved_by: str, reason: str | None = None):
        return await self._approval_gate.resolve_approval(request_id, status, resolved_by, reason)
