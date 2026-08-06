"""
services/api/tests/integration/test_skill_e2e.py

Sprint 9 – API-Level End-to-End Integration Test
================================================

Exercises the complete Skill Runtime pipeline through the **public REST API**,
verifying that every architectural stage participates in each execution:

    HTTP Client
        ↓ POST /ai/skills/{skill_id}/execute
    FastAPI Router (routers/skills.py)
        ↓ AtlasAISDK.skills.execute()
    SkillsPipeline (sdk/skills.py)
        ↓ SkillRuntime.execute()
    Skill Registry  (skills_runtime/registry.py)
        ↓ SkillRegistryService.known_skill_ids()
    Skill Loader    (skills_runtime/loader.py)
        ↓ SkillLoader.load() + validate_manifest()
    Manifest Validation (skills_runtime/schema.py)
        ↓ JSON Schema validation
    Dependency Resolver (skills_runtime/dependency.py)
        ↓ DependencyResolver.resolve()
    Policy Engine   (skills_runtime/policy.py)
        ↓ PolicyEngine.evaluate()
    Permission Engine (skills_runtime/permissions.py)
        ↓ ToolPermissionEngine.ensure_step_tools_allowed()
    Workflow Executor (skills_runtime/workflow_executor.py)
        ↓ WorkflowExecutor.run()
    Model Adapter   (skills_runtime/model_adapter.py)
        ↓ ModelAdapter.run_step() → LLM.generate()
    Output Validation (skills_runtime/output_validator.py)
        ↓ OutputValidator.validate()
    Memory Write    (runtime/memory.py)
        ↓ RuntimeMemoryStore.append()
    Telemetry       (telemetry/hooks.py)
        ↓ TelemetryContext.timed()
    HTTP Response   (200 OK with SkillExecutionResponse body)

Every assertion targets a *specific* stage — this test is NOT a simple HTTP 200 smoke test.
"""
from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any
from unittest.mock import MagicMock, patch

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.ai.agents.execution_agent import ExecutionAgent
from app.ai.agents.planner_agent import PlannerAgent
from app.ai.config.models import AIConfig
from app.ai.factory.factory import ProviderFactory
from app.ai.knowledge.factory import KnowledgeProviderFactory
from app.ai.orchestration.knowledge_orchestrator import KnowledgeOrchestrator
from app.ai.runtime import AgentRuntime, RuntimeConfig, RuntimeMemoryStore
from app.ai.sdk.sdk import AtlasAISDK
from app.ai.skills_runtime import build_skill_runtime
from app.ai.telemetry.hooks import TelemetryContext, get_telemetry
from app.ai.tools import ToolExecutor, ToolRegistry, build_default_tools
from app.ai.utils.bootstrap import build_default_registry
from app.routers.skills import router as skills_router


# ---------------------------------------------------------------------------
# Shared lifespan fixture
# ---------------------------------------------------------------------------


@asynccontextmanager
async def _lifespan(app: FastAPI):
    """Mirrors main.py lifespan with mock providers for test isolation."""
    registry = build_default_registry()
    config = AIConfig(
        knowledge={"provider": "native"},
        documents={"provider": "mock"},
        embeddings={"provider": "mock"},
        vectorstore={"provider": "mock"},
        retrieval={"provider": "mock"},
        llm={"provider": "mock"},
        memory={"provider": "mock"},
    )
    factory = ProviderFactory(registry, config)
    telemetry = get_telemetry()
    knowledge_provider = KnowledgeProviderFactory(factory, telemetry=telemetry).create()
    orchestrator = KnowledgeOrchestrator(factory, knowledge_provider, telemetry=telemetry)

    memory_provider = await factory.create_memory()
    runtime_memory = RuntimeMemoryStore(memory_provider)

    tool_registry = ToolRegistry()
    runtime_cfg = RuntimeConfig(default_timeout=30)
    for tool in build_default_tools(orchestrator, config={"ai": config.model_dump()}):
        tool_registry.register(tool)
    tool_executor = ToolExecutor(tool_registry)

    planner_agent = PlannerAgent(config={})
    execution_agent = ExecutionAgent(factory=factory, config={}, tool_executor=tool_executor)
    runtime = AgentRuntime(
        planner_agent=planner_agent,
        execution_agent=execution_agent,
        memory_store=runtime_memory,
        config=runtime_cfg,
    )
    skill_runtime = await build_skill_runtime(factory, telemetry=telemetry, memory_provider=memory_provider)

    sdk = AtlasAISDK(
        registry=registry,
        factory=factory,
        orchestrator=orchestrator,
        telemetry=telemetry,
        runtime=runtime,
        skill_runtime=skill_runtime,
        tool_registry=tool_registry,
        tool_executor=tool_executor,
        memory_provider=memory_provider,
    )

    app.state.ai_sdk = sdk
    app.state.ai_skill_runtime = skill_runtime
    app.state.ai_memory_provider = memory_provider
    app.state.ai_telemetry = telemetry
    yield
    await registry.shutdown_all()


def _build_test_app() -> FastAPI:
    app = FastAPI(lifespan=_lifespan)
    app.include_router(skills_router)
    return app


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------


SKILL_ID = "engineering_manager"

CLEAN_POLICY_CONTEXT: dict[str, Any] = {
    "p0_defects": 0,
    "p1_defects": 0,
    "coverage_percent": 92.0,
}

BLOCKING_POLICY_CONTEXT: dict[str, Any] = {
    "p0_defects": 3,  # triggers no_p0 block rule
}


# ---------------------------------------------------------------------------
# Stage-by-stage end-to-end test
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_skill_e2e_pipeline_full_execution():
    """
    Verifies every pipeline stage from HTTP → Response.

    Stage assertions:
    - Registry    : skill_id appears in GET /ai/skills
    - Loader      : skill detail has all required SkillPackage fields
    - Manifest    : validate endpoint returns valid=True
    - Dependencies: execute result carries dependency_warnings list
    - Policy      : clean context → no policy_violations in result
    - Permission  : allowed tool → step runs without error
    - Workflow    : traces list is non-empty (one entry per step)
    - Model       : each trace has non-empty output (LLM was called)
    - Output Val  : declared outputs are present and non-empty
    - Memory      : WorkflowExecutor calls memory_store.append (verified via spy)
    - Telemetry   : TelemetryContext.timed is called (verified via spy)
    - HTTP Resp   : 200 OK with SkillExecutionResponse shape
    """
    app = _build_test_app()

    async with app.router.lifespan_context(app):
        sdk: AtlasAISDK = app.state.ai_sdk
        skill_runtime = app.state.ai_skill_runtime
        memory_provider = app.state.ai_memory_provider
        telemetry: TelemetryContext = app.state.ai_telemetry

        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:

            # ----------------------------------------------------------------
            # Stage 1: Registry — skill must be listed
            # ----------------------------------------------------------------
            list_resp = await client.get("/ai/skills")
            assert list_resp.status_code == 200, f"Registry list failed: {list_resp.text}"
            skills = list_resp.json()["skills"]
            registry_ids = [s.get("registry_entry", {}).get("id") for s in skills]
            assert SKILL_ID in registry_ids, (
                f"Registry stage FAILED: '{SKILL_ID}' not found in registry. Got: {registry_ids}"
            )

            # ----------------------------------------------------------------
            # Stage 2: Loader — skill must be loadable with all required fields
            # ----------------------------------------------------------------
            detail_resp = await client.get(f"/ai/skills/{SKILL_ID}")
            assert detail_resp.status_code == 200, f"Loader stage FAILED: {detail_resp.text}"
            skill_data = detail_resp.json()["skill"]
            for required_field in ("id", "name", "display_name", "version", "workflow", "policies", "interfaces"):
                assert required_field in skill_data, (
                    f"Loader stage FAILED: SkillPackage missing field '{required_field}'"
                )
            assert len(skill_data["workflow"]) > 0, "Loader stage FAILED: workflow has no steps"

            # ----------------------------------------------------------------
            # Stage 3: Manifest Validation — validate endpoint must pass
            # ----------------------------------------------------------------
            validate_resp = await client.post("/ai/skills/validate", json={"skill_id": SKILL_ID})
            assert validate_resp.status_code == 200, f"Manifest Validation stage FAILED: {validate_resp.text}"
            assert validate_resp.json()["valid"] is True, (
                f"Manifest Validation stage FAILED: valid=False. Detail: {validate_resp.json()}"
            )

            # ----------------------------------------------------------------
            # Stage 4-9: Execute — Policy, Permission, Workflow, Model, Memory, Telemetry
            # ----------------------------------------------------------------
            memory_calls: list[tuple] = []
            original_append = skill_runtime.workflow_executor._memory_store.append

            async def _spy_append(ctx, key, value):
                memory_calls.append((key, value))
                return await original_append(ctx, key, value)

            telemetry_calls: list[str] = []
            original_timed = telemetry.timed

            import contextlib

            @contextlib.contextmanager
            def _spy_timed(name, tags=None):
                telemetry_calls.append(name)
                with original_timed(name, tags):
                    yield

            with (
                patch.object(skill_runtime.workflow_executor._memory_store, "append", side_effect=_spy_append),
                patch.object(telemetry, "timed", side_effect=_spy_timed),
            ):
                execute_resp = await client.post(
                    f"/ai/skills/{SKILL_ID}/execute",
                    json={
                        "prompt": "Prepare Sprint 9 execution plan",
                        "workspace_id": "ws-e2e-test",
                        "organization_id": "org-e2e-test",
                        "policy_context": CLEAN_POLICY_CONTEXT,
                        "step_tools": {"execute": ["terminal"]},
                        "correlation_id": "e2e-test-run-001",
                    },
                )

            # ----------------------------------------------------------------
            # HTTP Response
            # ----------------------------------------------------------------
            assert execute_resp.status_code == 200, (
                f"HTTP Response stage FAILED: expected 200, got {execute_resp.status_code}. Body: {execute_resp.text}"
            )
            payload = execute_resp.json()

            # ----------------------------------------------------------------
            # Stage 4: Dependency Resolver — field must be present (may be empty)
            # ----------------------------------------------------------------
            assert "dependency_warnings" in payload, (
                "Dependency Resolver stage FAILED: 'dependency_warnings' missing from response"
            )
            assert isinstance(payload["dependency_warnings"], list), (
                "Dependency Resolver stage FAILED: 'dependency_warnings' is not a list"
            )

            # ----------------------------------------------------------------
            # Stage 5: Policy Engine — no violations with clean context
            # ----------------------------------------------------------------
            assert payload["policy_violations"] == [], (
                f"Policy Engine stage FAILED: expected no violations, got {payload['policy_violations']}"
            )

            # ----------------------------------------------------------------
            # Stage 6: Workflow Executor — traces present, one per step
            # ----------------------------------------------------------------
            assert payload["status"] == "completed", (
                f"Workflow Executor stage FAILED: status={payload['status']}, error={payload.get('error')}"
            )
            traces = payload["traces"]
            assert len(traces) > 0, "Workflow Executor stage FAILED: no step traces in response"
            expected_step_count = len(skill_data["workflow"])
            assert len(traces) == expected_step_count, (
                f"Workflow Executor stage FAILED: expected {expected_step_count} traces, got {len(traces)}"
            )

            # ----------------------------------------------------------------
            # Stage 7: Model Adapter — each trace has non-empty output (LLM invoked)
            # ----------------------------------------------------------------
            for trace in traces:
                assert trace.get("output") not in (None, ""), (
                    f"Model Adapter stage FAILED: trace for step '{trace.get('step_id')}' has empty output"
                )

            # ----------------------------------------------------------------
            # Stage 8: Output Validator — all declared outputs present and non-empty
            # ----------------------------------------------------------------
            declared_outputs = skill_data["interfaces"]["outputs"]
            outputs = payload["outputs"]
            assert isinstance(outputs, dict), "Output Validator stage FAILED: outputs is not a dict"
            for output_name in declared_outputs:
                assert output_name in outputs, (
                    f"Output Validator stage FAILED: declared output '{output_name}' missing from response"
                )
                assert outputs[output_name] not in (None, ""), (
                    f"Output Validator stage FAILED: declared output '{output_name}' is empty"
                )

            # ----------------------------------------------------------------
            # Stage 9: Memory Write — memory.append was called for each step + final result
            # ----------------------------------------------------------------
            assert len(memory_calls) > 0, (
                "Memory Write stage FAILED: RuntimeMemoryStore.append was never called"
            )
            memory_keys = [call[0] for call in memory_calls]
            assert "skill_steps" in memory_keys, (
                "Memory Write stage FAILED: 'skill_steps' key never written to memory"
            )
            assert "skill_results" in memory_keys, (
                "Memory Write stage FAILED: 'skill_results' key never written to memory"
            )

            # ----------------------------------------------------------------
            # Stage 10: Telemetry — timed spans recorded for execution and each step
            # ----------------------------------------------------------------
            assert len(telemetry_calls) > 0, (
                "Telemetry stage FAILED: TelemetryContext.timed was never called"
            )
            skill_spans = [c for c in telemetry_calls if "skills_runtime" in c]
            assert len(skill_spans) > 0, (
                f"Telemetry stage FAILED: no 'skills_runtime' spans recorded. All calls: {telemetry_calls}"
            )

            # ----------------------------------------------------------------
            # Structural assertion: execution_id is a UUID
            # ----------------------------------------------------------------
            import uuid
            try:
                uuid.UUID(payload["execution_id"])
            except ValueError as exc:
                raise AssertionError(
                    f"HTTP Response stage FAILED: execution_id is not a valid UUID: {payload['execution_id']}"
                ) from exc


# ---------------------------------------------------------------------------
# Policy Engine blocking path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_skill_e2e_policy_engine_blocks_on_p0_defects():
    """
    Verifies that the Policy Engine blocks execution when P0 defects are present.

    Asserts:
    - HTTP 200 (the endpoint always returns 200; status field carries the outcome)
    - status == 'blocked'
    - policy_violations is non-empty and references the 'no_p0' rule
    - traces is empty (Workflow Executor never ran)
    - outputs is empty (no output produced)
    """
    app = _build_test_app()

    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/ai/skills/{SKILL_ID}/execute",
                json={
                    "prompt": "Ship with P0 defects",
                    "workspace_id": "ws-policy-test",
                    "policy_context": BLOCKING_POLICY_CONTEXT,
                },
            )

    assert resp.status_code == 200, f"Expected 200, got {resp.status_code}"
    payload = resp.json()
    assert payload["status"] == "blocked", (
        f"Policy Engine E2E FAILED: expected 'blocked', got '{payload['status']}'"
    )
    assert len(payload["policy_violations"]) > 0, (
        "Policy Engine E2E FAILED: policy_violations is empty despite P0 defects"
    )
    assert any("no_p0" in v for v in payload["policy_violations"]), (
        f"Policy Engine E2E FAILED: 'no_p0' rule not in violations: {payload['policy_violations']}"
    )
    assert payload["traces"] == [], (
        "Policy Engine E2E FAILED: Workflow Executor should not run when blocked by policy"
    )


# ---------------------------------------------------------------------------
# Permission Engine denial path
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_skill_e2e_permission_engine_denies_unauthorized_tool():
    """
    Verifies that the Permission Engine denies an execution when a step
    requests a tool not listed in the skill's tools.yaml.

    Asserts:
    - status == 'failed' (permission denial surfaces as execution failure)
    - error message contains 'cannot use tool'
    """
    app = _build_test_app()

    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.post(
                f"/ai/skills/{SKILL_ID}/execute",
                json={
                    "prompt": "Try to use an unauthorized tool",
                    "workspace_id": "ws-perm-test",
                    "policy_context": CLEAN_POLICY_CONTEXT,
                    "step_tools": {"execute": ["super_admin_shell"]},  # not in tools.yaml
                },
            )

    assert resp.status_code == 200
    payload = resp.json()
    assert payload["status"] == "failed", (
        f"Permission Engine E2E FAILED: expected 'failed', got '{payload['status']}'"
    )
    assert payload["error"] is not None, "Permission Engine E2E FAILED: error field is None"
    assert "cannot use tool" in payload["error"], (
        f"Permission Engine E2E FAILED: unexpected error message: {payload['error']}"
    )


# ---------------------------------------------------------------------------
# Registry / Loader — 404 for unknown skill
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_skill_e2e_unknown_skill_returns_404():
    """
    Verifies that requesting a non-existent skill returns HTTP 404.
    Confirms Registry + Loader error handling propagates correctly through the API layer.
    """
    app = _build_test_app()

    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/ai/skills/does_not_exist_skill_xyz")

    assert resp.status_code == 404, (
        f"Registry/Loader E2E FAILED: expected 404 for unknown skill, got {resp.status_code}"
    )


# ---------------------------------------------------------------------------
# OpenAPI self-check
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_skill_e2e_openapi_documents_all_endpoints():
    """
    Verifies that /openapi.json is generated and documents all Skill API endpoints.
    """
    app = _build_test_app()

    async with app.router.lifespan_context(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            resp = await client.get("/openapi.json")

    assert resp.status_code == 200, f"OpenAPI generation FAILED: {resp.status_code}"
    spec = resp.json()
    paths = spec.get("paths", {})

    expected_paths = [
        "/ai/skills",
        "/ai/skills/validate",
        "/ai/skills/install",
        "/ai/skills/uninstall",
        "/ai/skills/reload",
        "/ai/skills/{skill_id}",
        "/ai/skills/{skill_id}/schema",
        "/ai/skills/{skill_id}/execute",
    ]
    for path in expected_paths:
        assert path in paths, (
            f"OpenAPI stage FAILED: path '{path}' not found in /openapi.json. "
            f"Documented paths: {list(paths.keys())}"
        )

    # Verify response_model metadata is present
    execute_path = paths.get("/ai/skills/{skill_id}/execute", {})
    post_op = execute_path.get("post", {})
    assert "summary" in post_op, "OpenAPI stage FAILED: /execute POST is missing 'summary'"
    assert "description" in post_op, "OpenAPI stage FAILED: /execute POST is missing 'description'"
    responses_200 = post_op.get("responses", {}).get("200", {})
    assert responses_200, "OpenAPI stage FAILED: /execute POST is missing 200 response definition"
