import pytest
from app.ai.skills_runtime.handoff import HandoffProtocol
from app.ai.telemetry.hooks import TelemetryContext

def test_handoff_contract_mapping():
    handoff = HandoffProtocol()
    
    # Simulate BE outputting backend_code_diff
    handoff.create_handoff(
        from_skill="backend_engineer",
        to_skill="*",
        payload={"backend_code_diff": "def test(): pass"},
        trigger="completion",
        execution_id="exec_1"
    )
    
    # Simulate FE outputting frontend_code_diff
    handoff.create_handoff(
        from_skill="frontend_engineer",
        to_skill="*",
        payload={"frontend_code_diff": "<div></div>"},
        trigger="completion",
        execution_id="exec_1"
    )
    
    available = {
        "backend_engineer": {"backend_code_diff": "def test(): pass"},
        "frontend_engineer": {"frontend_code_diff": "<div></div>"}
    }
    
    # Reviewer requires both
    resolved = handoff.resolve_inputs(
        target_skill="code_reviewer",
        execution_id="exec_1",
        available_outputs=available,
        requires=["backend_code_diff", "frontend_code_diff"]
    )
    
    assert "backend_code_diff" in resolved
    assert "frontend_code_diff" in resolved
    assert resolved["backend_code_diff"] == "def test(): pass"
