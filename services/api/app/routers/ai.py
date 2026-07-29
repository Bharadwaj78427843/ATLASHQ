from fastapi import APIRouter, Depends
from typing import Any
from fastapi.responses import StreamingResponse

from app.dependencies import get_ai_sdk
from app.ai.sdk.sdk import AtlasAISDK


router = APIRouter(prefix="/api/ai", tags=["AI Platform"])


@router.get("/health")
async def health(sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.health.check()


@router.get("/providers")
async def providers(sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    listed = await sdk.providers.list_providers()
    listed["knowledge"] = await sdk.knowledge.status()
    return listed


@router.get("/config")
async def config(sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    # Placeholder config endpoint
    return {"status": "ok", "config": {}}


from pydantic import BaseModel

class ChatRequest(BaseModel):
    prompt: str
    workspace_id: str | None = None

@router.post("/chat")
async def chat(request: ChatRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.chat.chat(prompt=request.prompt, workspace_id=request.workspace_id)


@router.post("/chat/stream")
async def chat_stream(request: ChatRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> StreamingResponse:
    async def event_stream():
        async for chunk in sdk.chat.chat_stream(prompt=request.prompt, workspace_id=request.workspace_id):
            yield f"data: {chunk}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


class KnowledgeSearchRequest(BaseModel):
    query: str
    workspace_id: str | None = None
    top_k: int = 5

@router.post("/knowledge/search")
async def knowledge_search(request: KnowledgeSearchRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.knowledge.search(query=request.query, workspace_id=request.workspace_id, top_k=request.top_k)


class KnowledgeUploadRequest(BaseModel):
    document_id: str
    collection: str = "default"

@router.post("/knowledge/upload")
async def knowledge_upload(request: KnowledgeUploadRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.knowledge.upload(document_id=request.document_id, collection=request.collection)


class KnowledgeSyncRequest(BaseModel):
    workspace_id: str
    source_type: str
    source_uri: str
    branch: str | None = None


@router.post("/knowledge/sync")
async def knowledge_sync(request: KnowledgeSyncRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.knowledge.sync(
        workspace_id=request.workspace_id,
        source_type=request.source_type,
        source_uri=request.source_uri,
        branch=request.branch,
    )


@router.get("/knowledge/status")
async def knowledge_status(sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.knowledge.status()


@router.post("/prompts/render")
async def prompts_render() -> dict[str, Any]:
    return {"status": "mocked render"}


class AgentExecuteRequest(BaseModel):
    prompt: str
    workspace_id: str | None = None
    organization_id: str | None = None
    user_id: str | None = None


@router.post("/agents/execute")
async def agents_execute(request: AgentExecuteRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.agents.execute(
        prompt=request.prompt,
        workspace_id=request.workspace_id,
        organization_id=request.organization_id,
        user_id=request.user_id,
    )


class AgentPlanRequest(BaseModel):
    prompt: str
    workspace_id: str | None = None
    organization_id: str | None = None
    user_id: str | None = None


@router.post("/agents/plan")
async def agents_plan(request: AgentPlanRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.agents.plan(
        prompt=request.prompt,
        workspace_id=request.workspace_id,
        organization_id=request.organization_id,
        user_id=request.user_id,
    )


@router.get("/agents/status/{execution_id}")
async def agents_status(execution_id: str, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.agents.status(execution_id)


@router.get("/agents/events/{execution_id}")
async def agents_events(execution_id: str, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> StreamingResponse:
    async def event_stream():
        events = await sdk.agents.events(execution_id)
        for event in events["events"]:
            yield f"data: {event}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


class AgentCancelRequest(BaseModel):
    execution_id: str


@router.post("/agents/cancel")
async def agents_cancel(request: AgentCancelRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.agents.cancel(request.execution_id)


class AgentResumeRequest(BaseModel):
    execution_id: str


@router.post("/agents/resume")
async def agents_resume(request: AgentResumeRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.agents.resume(request.execution_id)


@router.get("/tools")
async def tools_list(sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.tools.list()


class ToolExecuteRequest(BaseModel):
    args: dict[str, Any] = {}
    workspace_id: str | None = None
    organization_id: str | None = None
    user_id: str | None = None
    execution_id: str | None = None


@router.post("/tools/{tool_name}")
async def tools_execute(tool_name: str, request: ToolExecuteRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.tools.execute(
        tool_name,
        request.args,
        workspace_id=request.workspace_id,
        organization_id=request.organization_id,
        user_id=request.user_id,
        execution_id=request.execution_id,
    )


@router.get("/memory")
async def memory_get(
    execution_id: str,
    workspace_id: str | None = None,
    key: str = "results",
    sdk: AtlasAISDK = Depends(get_ai_sdk),
) -> dict[str, Any]:
    return await sdk.memory.get(workspace_id=workspace_id, execution_id=execution_id, key=key)


class MemoryClearRequest(BaseModel):
    scope: str


@router.post("/memory/clear")
async def memory_clear(request: MemoryClearRequest, sdk: AtlasAISDK = Depends(get_ai_sdk)) -> dict[str, Any]:
    return await sdk.memory.clear(request.scope)
