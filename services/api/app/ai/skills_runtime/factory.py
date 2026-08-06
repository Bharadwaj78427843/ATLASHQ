from __future__ import annotations

from app.ai.factory.factory import ProviderFactory
from app.ai.interfaces.memory import MemoryProvider
from app.ai.runtime.memory import RuntimeMemoryStore
from app.ai.skills_runtime.dependency import DependencyResolver
from app.ai.skills_runtime.loader import SkillLoader
from app.ai.skills_runtime.model_adapter import ModelAdapter
from app.ai.skills_runtime.output_validator import OutputValidator
from app.ai.skills_runtime.permissions import ToolPermissionEngine
from app.ai.skills_runtime.policy import PolicyEngine
from app.ai.skills_runtime.registry import SkillRegistryService
from app.ai.skills_runtime.runtime import SkillRuntime
from app.ai.skills_runtime.workflow_executor import WorkflowExecutor
from app.ai.telemetry.hooks import TelemetryContext, get_telemetry


async def build_skill_runtime(
    factory: ProviderFactory,
    telemetry: TelemetryContext | None = None,
    memory_provider: MemoryProvider | None = None,
) -> SkillRuntime:
    telemetry_ctx = telemetry or get_telemetry()
    memory_provider = memory_provider or await factory.create_memory()
    memory_store = RuntimeMemoryStore(memory_provider)

    registry = SkillRegistryService()
    loader = SkillLoader(registry)
    dependency_resolver = DependencyResolver(registry, loader)
    policy_engine = PolicyEngine()
    permission_engine = ToolPermissionEngine()
    model_adapter = ModelAdapter(factory)
    workflow_executor = WorkflowExecutor(
        model_adapter=model_adapter,
        permission_engine=permission_engine,
        memory_store=memory_store,
        telemetry=telemetry_ctx,
    )
    output_validator = OutputValidator()

    return SkillRuntime(
        registry=registry,
        loader=loader,
        dependency_resolver=dependency_resolver,
        policy_engine=policy_engine,
        workflow_executor=workflow_executor,
        output_validator=output_validator,
        telemetry=telemetry_ctx,
    )
