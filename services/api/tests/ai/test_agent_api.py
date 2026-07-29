import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.mark.asyncio
async def test_agent_runtime_endpoints_smoke():
    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            plan = await client.post("/api/ai/agents/plan", json={"prompt": "Analyze auth", "workspace_id": "w1"})
            assert plan.status_code == 200
            plan_json = plan.json()
            assert "execution_id" in plan_json

            execute = await client.post("/api/ai/agents/execute", json={"prompt": "Analyze auth", "workspace_id": "w1"})
            assert execute.status_code == 200
            execute_json = execute.json()
            assert "execution_id" in execute_json

            status = await client.get(f"/api/ai/agents/status/{execute_json['execution_id']}")
            assert status.status_code == 200

            tools = await client.get("/api/ai/tools")
            assert tools.status_code == 200
            assert "tools" in tools.json()

            tool_exec = await client.post(
                "/api/ai/tools/workspace_tool",
                json={"args": {}, "workspace_id": "w1"},
            )
            assert tool_exec.status_code == 200

            memory = await client.get(
                "/api/ai/memory",
                params={"execution_id": execute_json["execution_id"], "workspace_id": "w1", "key": "results"},
            )
            assert memory.status_code == 200

            cancel = await client.post("/api/ai/agents/cancel", json={"execution_id": execute_json["execution_id"]})
            assert cancel.status_code == 200
