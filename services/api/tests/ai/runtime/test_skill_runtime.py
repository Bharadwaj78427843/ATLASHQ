import pytest

from app.ai.config.models import AIConfig
from app.ai.factory.factory import ProviderFactory
from app.ai.skills_runtime import SkillExecutionRequest, SkillExecutionStatus, build_skill_runtime
from app.ai.utils.bootstrap import build_default_registry


@pytest.mark.asyncio
async def test_skill_runtime_executes_engineering_manager_package():
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
    runtime = await build_skill_runtime(factory)

    result = await runtime.execute(
        SkillExecutionRequest(
            skill_id="engineering_manager",
            prompt="Prepare Sprint 9 execution plan",
            workspace_id="w1",
            policy_context={"p0_defects": 0, "p1_defects": 0},
            step_tools={"execute": ["terminal"]},
        )
    )

    assert result.status == SkillExecutionStatus.COMPLETED
    assert "sprint_status_assessment" in result.outputs
    assert "prioritized_execution_plan" in result.outputs
    assert "release_readiness_report" in result.outputs
    assert len(result.traces) > 0


@pytest.mark.asyncio
async def test_skill_runtime_blocks_on_policy_violation():
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
    runtime = await build_skill_runtime(factory)

    result = await runtime.execute(
        SkillExecutionRequest(
            skill_id="engineering_manager",
            prompt="Ship Sprint 9",
            workspace_id="w1",
            policy_context={"p0_defects": 1},
        )
    )

    assert result.status == SkillExecutionStatus.BLOCKED
    assert result.policy_violations


@pytest.mark.asyncio
async def test_skill_runtime_denies_disallowed_tool():
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
    runtime = await build_skill_runtime(factory)

    result = await runtime.execute(
        SkillExecutionRequest(
            skill_id="engineering_manager",
            prompt="Run execution",
            workspace_id="w1",
            policy_context={"p0_defects": 0, "p1_defects": 0},
            step_tools={"execute": ["super_admin_shell"]},
        )
    )

    assert result.status == SkillExecutionStatus.FAILED
    assert result.error is not None
    assert "cannot use tool" in result.error
