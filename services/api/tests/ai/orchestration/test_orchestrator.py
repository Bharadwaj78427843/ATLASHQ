import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from app.ai.skills_runtime.orchestrator import SkillOrchestrator, OrchestrationGraph, OrchestrationNode, DAGStateTracker
from app.ai.skills_runtime.models import SkillExecutionRequest, SkillExecutionResult, SkillExecutionStatus
from app.ai.interfaces.memory import MemoryProvider

@pytest.fixture
def mock_runtime():
    runtime = MagicMock()
    runtime.loader = MagicMock()
    skill_mock = MagicMock()
    skill_mock.interfaces.requires = []
    runtime.loader.load.return_value = skill_mock
    
    async def mock_execute(request):
        return SkillExecutionResult(
            execution_id=request.correlation_id,
            skill_id=request.skill_id,
            status=SkillExecutionStatus.COMPLETED,
            outputs={f"{request.skill_id}_output": "success"},
            traces=[],
            policy_violations=[],
            dependency_warnings=[]
        )
    runtime.execute = AsyncMock(side_effect=mock_execute)
    
    memory_mock = AsyncMock(spec=MemoryProvider)
    runtime.memory_provider = memory_mock
    
    return runtime

@pytest.fixture
def mock_handoff():
    handoff = MagicMock()
    handoff.resolve_inputs.return_value = {}
    handoff.create_handoff = MagicMock()
    return handoff

@pytest.fixture
def mock_approval():
    approval = AsyncMock()
    
    class ApprovalResult:
        status = "APPROVED"
        resolved_by = "test_user"
        resolution_reason = None
        
    approval.wait_for_approval.return_value = ApprovalResult()
    
    class RequestResult:
        id = "123"
        
    approval.request_approval.return_value = RequestResult()
    return approval

@pytest.fixture
def orchestrator(mock_runtime, mock_handoff, mock_approval):
    return SkillOrchestrator(
        skill_runtime=mock_runtime,
        handoff_protocol=mock_handoff,
        approval_gate=mock_approval,
        telemetry=MagicMock()
    )

def test_orchestrator_cycle_detection(orchestrator):
    node_a = OrchestrationNode(id="A", type="SKILL", depends_on=["B"])
    node_b = OrchestrationNode(id="B", type="SKILL", depends_on=["A"])
    graph = OrchestrationGraph(nodes=[node_a, node_b])
    
    with pytest.raises(ValueError, match="Cycle detected"):
        orchestrator._validate_dag(graph)

@pytest.mark.asyncio
async def test_orchestrator_e2e_dag(orchestrator):
    node_em = OrchestrationNode(id="EM", type="SKILL", skill_id="engineering_manager")
    node_arch = OrchestrationNode(id="ARCH", type="SKILL", skill_id="architect", depends_on=["EM"])
    node_be = OrchestrationNode(id="BE", type="SKILL", skill_id="backend_engineer", depends_on=["ARCH"], parallelizable=True)
    node_fe = OrchestrationNode(id="FE", type="SKILL", skill_id="frontend_engineer", depends_on=["ARCH"], parallelizable=True)
    
    graph = OrchestrationGraph(nodes=[node_em, node_arch, node_be, node_fe])
    base_request = SkillExecutionRequest(skill_id="orchestrator", prompt="test", correlation_id="test_exec_1")
    
    result = await orchestrator.execute_graph(graph, base_request)
    
    assert result.status == SkillExecutionStatus.COMPLETED
    assert result.execution_id == "test_exec_1"
    assert "EM" in result.node_results
    assert "ARCH" in result.node_results
    assert "BE" in result.node_results
    assert "FE" in result.node_results
    
    # Assert Memory tracker was called
    orchestrator._skill_runtime.memory_provider.put.assert_called()

@pytest.mark.asyncio
async def test_orchestrator_fallback_recovery(orchestrator):
    # Make backend fail 3 times to trigger fallback approval
    fail_mock = AsyncMock(return_value=SkillExecutionResult(
        execution_id="test", skill_id="be", status=SkillExecutionStatus.FAILED,
        outputs={}, traces=[], policy_violations=[], dependency_warnings=[]
    ))
    orchestrator._skill_runtime.execute = fail_mock
    
    node_be = OrchestrationNode(id="BE", type="SKILL", skill_id="backend_engineer")
    graph = OrchestrationGraph(nodes=[node_be])
    
    # Wait for approval will return APPROVED, so it tries once more then returns failure
    result = await orchestrator.execute_graph(graph, SkillExecutionRequest(skill_id="orchestrator", prompt="fail test", correlation_id="fail_1"))
    
    assert result.status == SkillExecutionStatus.FAILED
    assert orchestrator._approval_gate.request_approval.call_count == 1
