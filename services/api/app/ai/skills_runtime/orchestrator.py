"""
app/ai/skills_runtime/orchestrator.py

Execution engine for multi-skill declarative DAGs (Directed Acyclic Graphs).
"""
from __future__ import annotations

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any

from app.ai.skills_runtime.models import SkillExecutionRequest, SkillExecutionResult, SkillExecutionStatus
from app.ai.skills_runtime.runtime import SkillRuntime
from app.ai.skills_runtime.handoff import HandoffProtocol
from app.ai.skills_runtime.approval import ApprovalGate
from app.ai.telemetry.hooks import TelemetryContext
from app.ai.telemetry.hooks import TelemetryContext
from app.ai.interfaces.memory import MemoryKey, MemoryRecord, MemoryProvider

logger = logging.getLogger(__name__)


@dataclass
class OrchestrationNode:
    id: str
    type: str # "SKILL", "APPROVAL", "GATE"
    skill_id: str | None = None
    action: str | None = None  # for approvals
    risk_level: str | None = None # for approvals
    depends_on: list[str] = field(default_factory=list)
    parallelizable: bool = False


@dataclass
class OrchestrationGraph:
    nodes: list[OrchestrationNode]


@dataclass
class OrchestrationResult:
    execution_id: str
    status: SkillExecutionStatus
    node_results: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

class DAGStateTracker:
    def __init__(self, memory_provider, execution_id: str):
        self.memory = memory_provider
        self.execution_id = execution_id
        self.key = MemoryKey(scope="organization:dag_state", identifier=execution_id)
        self.state = {"nodes": {}, "status": "RUNNING"}
        
    async def update_node(self, node_id: str, status: str, result: Any = None, error: str = None):
        if node_id not in self.state["nodes"]:
            self.state["nodes"][node_id] = {}
        self.state["nodes"][node_id].update({"status": status, "result": result, "error": error})
        await self.save()
        
    async def update_graph(self, status: str):
        self.state["status"] = status
        await self.save()
        
    async def save(self):
        await self.memory.put(MemoryRecord(key=self.key, value=self.state))


class SkillOrchestrator:
    def __init__(
        self,
        skill_runtime: SkillRuntime,
        handoff_protocol: HandoffProtocol,
        approval_gate: ApprovalGate,
        telemetry: TelemetryContext,
        memory_provider: MemoryProvider
    ) -> None:
        self._skill_runtime = skill_runtime
        self._handoff_protocol = handoff_protocol
        self._approval_gate = approval_gate
        self._telemetry = telemetry
        self._memory_provider = memory_provider

    def _validate_dag(self, graph: OrchestrationGraph) -> None:
        """Validate that the graph has no cycles."""
        visited = set()
        path = set()
        
        node_map = {n.id: n for n in graph.nodes}
        
        def visit(node_id: str) -> None:
            if node_id in path:
                raise ValueError(f"Cycle detected in orchestration graph at node {node_id}")
            if node_id in visited:
                return
                
            path.add(node_id)
            node = node_map.get(node_id)
            if node:
                for dep in node.depends_on:
                    visit(dep)
            path.remove(node_id)
            visited.add(node_id)
            
        for node in graph.nodes:
            visit(node.id)

    async def _run_skill_node(
        self, 
        node: OrchestrationNode, 
        request: SkillExecutionRequest,
        available_outputs: dict[str, dict[str, Any]]
    ) -> SkillExecutionResult:
        if not node.skill_id:
            raise ValueError(f"Skill node {node.id} missing skill_id")
            
        skill = self._skill_runtime.loader.load(node.skill_id)
        
        # Resolve inputs using handoff protocol
        resolved_inputs = self._handoff_protocol.resolve_inputs(
            node.skill_id, request.correlation_id or "unknown", available_outputs, skill.interfaces.requires
        )
        
        # Inject resolved inputs into memory or metadata for the skill
        node_request = SkillExecutionRequest(
            skill_id=node.skill_id,
            prompt=request.prompt,
            workspace_id=request.workspace_id,
            organization_id=request.organization_id,
            user_id=request.user_id,
            project_id=request.project_id,
            repository_id=request.repository_id,
            session_id=request.session_id,
            metadata={**request.metadata, "resolved_inputs": resolved_inputs},
            policy_context=request.policy_context,
            permissions=request.permissions,
            memory=request.memory,
            configuration=request.configuration,
            correlation_id=request.correlation_id
        )
        
        result = await self._skill_runtime.execute(node_request)
        
        # Record handoffs
        for output_key, output_value in result.outputs.items():
            self._handoff_protocol.create_handoff(
                from_skill=node.skill_id,
                to_skill="*", # wildcard until consumed
                payload={output_key: output_value},
                trigger="completion",
                execution_id=result.execution_id
            )
            
        return result

    async def _run_skill_node_with_retry(
        self,
        node: OrchestrationNode,
        request: SkillExecutionRequest,
        available_outputs: dict[str, dict[str, Any]],
        tracker: DAGStateTracker
    ) -> SkillExecutionResult:
        max_retries = 2
        for attempt in range(max_retries + 1):
            await tracker.update_node(node.id, "RUNNING")
            try:
                res = await self._run_skill_node(node, request, available_outputs)
                if res.status == SkillExecutionStatus.COMPLETED:
                    await tracker.update_node(node.id, "COMPLETED", res.outputs)
                    return res
                else:
                    await tracker.update_node(node.id, "FAILED", error=res.error)
                    raise ValueError(f"Skill execution failed: {res.error}")
            except Exception as e:
                await tracker.update_node(node.id, "FAILED", error=str(e))
                if attempt == max_retries:
                    # Fallback to human intervention
                    try:
                        await tracker.update_node(node.id, "WAITING_APPROVAL")
                        approval_res = await self._run_approval_node(
                            OrchestrationNode(id=f"{node.id}_recovery", type="APPROVAL", action="retry_failed_node", risk_level="high"),
                            request.correlation_id or "unknown"
                        )
                        if approval_res["status"] == "APPROVED":
                            continue # try once more if approved
                        else:
                            break
                    except Exception as fallback_e:
                        raise ValueError(f"Node {node.id} failed and fallback rejected: {fallback_e}")
                
        return SkillExecutionResult(execution_id=request.correlation_id, skill_id=node.skill_id, status=SkillExecutionStatus.FAILED, outputs={}, traces=[], policy_violations=[], dependency_warnings=[])


    async def _run_approval_node(
        self,
        node: OrchestrationNode,
        execution_id: str
    ) -> dict[str, Any]:
        if not node.action or not node.risk_level:
            raise ValueError(f"Approval node {node.id} missing action or risk_level")
            
        request = await self._approval_gate.request_approval(
            execution_id=execution_id,
            skill_id="orchestrator",
            action=node.action,
            risk_level=node.risk_level,
            requires_reason=True
        )
        
        resolved = await self._approval_gate.wait_for_approval(str(request.id))
        
        if resolved.status == "REJECTED":
            raise ValueError(f"Approval {request.id} rejected: {resolved.resolution_reason}")
            
        return {"status": resolved.status, "approved_by": resolved.resolved_by}

    async def execute_graph(
        self,
        graph: OrchestrationGraph,
        base_request: SkillExecutionRequest
    ) -> OrchestrationResult:
        self._validate_dag(graph)
        
        execution_id = base_request.correlation_id or "unknown"
        tracker = DAGStateTracker(self._memory_provider, execution_id)
        
        node_results: dict[str, Any] = {}
        available_outputs: dict[str, dict[str, Any]] = {}
        
        # Initialize tracker
        for n in graph.nodes:
            await tracker.update_node(n.id, "PENDING")

        
        # Group nodes by layers (topological sort)
        node_map = {n.id: n for n in graph.nodes}
        indegree = {n.id: len(n.depends_on) for n in graph.nodes}
        
        queue = [nid for nid, d in indegree.items() if d == 0]
        
        while queue:
            current_batch = []
            for _ in range(len(queue)):
                node_id = queue.pop(0)
                current_batch.append(node_map[node_id])
                
            # Execute batch
            # We can parallelize nodes in the same batch if they are marked parallelizable
            parallel_tasks = []
            sequential_tasks = []
            
            for node in current_batch:
                if node.parallelizable:
                    parallel_tasks.append(node)
                else:
                    sequential_tasks.append(node)
                    
            # Run sequential
            for node in sequential_tasks:
                try:
                    if node.type == "SKILL":
                        res = await self._run_skill_node_with_retry(node, base_request, available_outputs, tracker)
                        node_results[node.id] = res
                        if res.status != SkillExecutionStatus.COMPLETED:
                            await tracker.update_graph("FAILED")
                            return OrchestrationResult(execution_id, res.status, node_results, res.error)
                        available_outputs[node.skill_id or node.id] = res.outputs
                    elif node.type == "APPROVAL":
                        await tracker.update_node(node.id, "WAITING_APPROVAL")
                        res = await self._run_approval_node(node, execution_id)
                        await tracker.update_node(node.id, "COMPLETED", res)
                        node_results[node.id] = res
                except Exception as e:
                    await tracker.update_graph("FAILED")
                    return OrchestrationResult(execution_id, SkillExecutionStatus.FAILED, node_results, str(e))

                    
            # Run parallel
            if parallel_tasks:
                async def _run_parallel(n: OrchestrationNode) -> tuple[str, Any]:
                    if n.type == "SKILL":
                        return n.id, await self._run_skill_node_with_retry(n, base_request, available_outputs, tracker)
                    elif n.type == "APPROVAL":
                        await tracker.update_node(n.id, "WAITING_APPROVAL")
                        res = await self._run_approval_node(n, execution_id)
                        await tracker.update_node(n.id, "COMPLETED", res)
                        return n.id, res
                    return n.id, None
                    
                results = await asyncio.gather(*[_run_parallel(n) for n in parallel_tasks], return_exceptions=True)
                for res in results:
                    if isinstance(res, Exception):
                        await tracker.update_graph("FAILED")
                        return OrchestrationResult(execution_id, SkillExecutionStatus.FAILED, node_results, str(res))
                    node_id, r = res
                    node_results[node_id] = r
                    if isinstance(r, SkillExecutionResult):
                        if r.status != SkillExecutionStatus.COMPLETED:
                            await tracker.update_graph("FAILED")
                            return OrchestrationResult(execution_id, r.status, node_results, r.error)
                        node = node_map[node_id]
                        available_outputs[node.skill_id or node.id] = r.outputs

            # Update indegrees for next layer
            for node in current_batch:
                for n in graph.nodes:
                    if node.id in n.depends_on:
                        indegree[n.id] -= 1
                        if indegree[n.id] == 0:
                            queue.append(n.id)
                            
        await tracker.update_graph("COMPLETED")
        return OrchestrationResult(
            execution_id=execution_id,
            status=SkillExecutionStatus.COMPLETED,
            node_results=node_results
        )
