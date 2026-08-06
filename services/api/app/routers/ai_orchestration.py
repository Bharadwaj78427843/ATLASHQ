from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Any, List
from app.dependencies import get_ai_skill_orchestrator, get_db
from app.ai.skills_runtime.orchestrator import SkillOrchestrator, OrchestrationGraph, OrchestrationNode
from app.ai.skills_runtime.models import SkillExecutionRequest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.memory import DBMemoryRecord

router = APIRouter(prefix="/ai/orchestration", tags=["AI Orchestration"])

class NodeDef(BaseModel):
    id: str
    type: str
    skill_id: str | None = None
    action: str | None = None
    risk_level: str | None = None
    depends_on: List[str] = []
    parallelizable: bool = False

class GraphDef(BaseModel):
    nodes: List[NodeDef]

class ExecuteGraphRequest(BaseModel):
    graph: GraphDef
    base_request: dict

@router.post("/execute")
async def execute_graph(req: ExecuteGraphRequest, background_tasks: BackgroundTasks, orchestrator: SkillOrchestrator = Depends(get_ai_skill_orchestrator)):
    import uuid
    execution_id = req.base_request.get("correlation_id", str(uuid.uuid4()))
    
    graph = OrchestrationGraph(
        nodes=[
            OrchestrationNode(
                id=n.id,
                type=n.type,
                skill_id=n.skill_id,
                action=n.action,
                risk_level=n.risk_level,
                depends_on=n.depends_on,
                parallelizable=n.parallelizable
            ) for n in req.graph.nodes
        ]
    )
    
    # We rebuild the base request
    base = SkillExecutionRequest(
        skill_id="orchestrator",
        prompt=req.base_request.get("prompt", ""),
        correlation_id=execution_id
    )
    
    async def run_in_background():
        try:
            await orchestrator.execute_graph(graph, base)
        except Exception as e:
            print(f"Orchestrator Background Error: {e}")
            
    background_tasks.add_task(run_in_background)
    
    return {
        "execution_id": execution_id,
        "status": "QUEUED"
    }

@router.get("/{execution_id}")
async def get_execution_state(execution_id: str, session: AsyncSession = Depends(get_db)):
    stmt = select(DBMemoryRecord).where(
        DBMemoryRecord.scope == "organization:dag_state",
        DBMemoryRecord.identifier == execution_id
    )
    res = await session.execute(stmt)
    record = res.scalar_one_or_none()
    
    if not record:
        return {
            "status": "QUEUED",
            "nodes": {}
        }
        
    return record.value

