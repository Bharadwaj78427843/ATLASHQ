"""
tests/ai/test_registry.py

Sprint 5 — Provider registry: registration, discovery, lazy loading,
resolution/caching, runtime switching, health monitoring, dependency graph.
"""
import pytest

from app.ai.exceptions.errors import ConfigurationError, ProviderNotFoundError
from app.ai.interfaces.base import HealthCheckResult, HealthStatus, ProviderCapabilities
from app.ai.llm.mock import MockLLMProvider
from app.ai.registry.registry import ProviderRegistry
from app.ai.registry.types import ProviderCategory


@pytest.fixture
def registry() -> ProviderRegistry:
    return ProviderRegistry()


def test_register_and_discover(registry: ProviderRegistry):
    registry.register(ProviderCategory.LLM, "mock", provider_cls=MockLLMProvider)
    assert registry.discover(ProviderCategory.LLM) == ["mock"]
    assert registry.is_registered(ProviderCategory.LLM, "mock")
    assert not registry.is_registered(ProviderCategory.LLM, "openai")


def test_register_requires_exactly_one_source(registry: ProviderRegistry):
    with pytest.raises(ConfigurationError):
        registry.register(ProviderCategory.LLM, "mock")
    with pytest.raises(ConfigurationError):
        registry.register(
            ProviderCategory.LLM, "mock", provider_cls=MockLLMProvider, module_path="a:B"
        )


def test_duplicate_registration_raises_unless_replace(registry: ProviderRegistry):
    registry.register(ProviderCategory.LLM, "mock", provider_cls=MockLLMProvider)
    with pytest.raises(ConfigurationError):
        registry.register(ProviderCategory.LLM, "mock", provider_cls=MockLLMProvider)
    registry.register(ProviderCategory.LLM, "mock", provider_cls=MockLLMProvider, replace=True)


@pytest.mark.asyncio
async def test_resolve_returns_initialized_and_cached_instance(registry: ProviderRegistry):
    registry.register(ProviderCategory.LLM, "mock", provider_cls=MockLLMProvider)
    instance_a = await registry.resolve(ProviderCategory.LLM, "mock")
    instance_b = await registry.resolve(ProviderCategory.LLM, "mock")
    assert instance_a is instance_b
    assert instance_a.is_initialized


@pytest.mark.asyncio
async def test_resolve_unknown_provider_raises(registry: ProviderRegistry):
    with pytest.raises(ProviderNotFoundError):
        await registry.resolve(ProviderCategory.LLM, "nonexistent")


@pytest.mark.asyncio
async def test_lazy_loading_via_module_path(registry: ProviderRegistry):
    registry.register(ProviderCategory.LLM, "mock", module_path="app.ai.llm.mock:MockLLMProvider")
    instance = await registry.resolve(ProviderCategory.LLM, "mock")
    assert isinstance(instance, MockLLMProvider)


@pytest.mark.asyncio
async def test_runtime_switching(registry: ProviderRegistry):
    class OtherMockLLM(MockLLMProvider):
        provider_name = "other-mock"

    registry.register(ProviderCategory.LLM, "mock", provider_cls=MockLLMProvider)
    registry.register(ProviderCategory.LLM, "other-mock", provider_cls=OtherMockLLM)

    registry.set_active(ProviderCategory.LLM, "mock")
    assert registry.get_active_name(ProviderCategory.LLM) == "mock"
    active = await registry.get_active(ProviderCategory.LLM)
    assert isinstance(active, MockLLMProvider)

    registry.set_active(ProviderCategory.LLM, "other-mock")
    active = await registry.get_active(ProviderCategory.LLM)
    assert isinstance(active, OtherMockLLM)


def test_set_active_unregistered_raises(registry: ProviderRegistry):
    with pytest.raises(ProviderNotFoundError):
        registry.set_active(ProviderCategory.LLM, "nonexistent")


@pytest.mark.asyncio
async def test_get_active_without_selection_raises(registry: ProviderRegistry):
    with pytest.raises(ConfigurationError):
        await registry.get_active(ProviderCategory.LLM)


@pytest.mark.asyncio
async def test_capabilities_lookup(registry: ProviderRegistry):
    registry.register(ProviderCategory.LLM, "mock", provider_cls=MockLLMProvider)
    caps = await registry.capabilities(ProviderCategory.LLM, "mock")
    assert isinstance(caps, ProviderCapabilities)
    assert caps.supports("chat")


@pytest.mark.asyncio
async def test_health_reports_unknown_before_resolve_and_healthy_after(registry: ProviderRegistry):
    registry.register(ProviderCategory.LLM, "mock", provider_cls=MockLLMProvider)

    before = await registry.health(ProviderCategory.LLM, "mock")
    assert before.status == HealthStatus.UNKNOWN

    await registry.resolve(ProviderCategory.LLM, "mock")
    after = await registry.health(ProviderCategory.LLM, "mock")
    assert isinstance(after, HealthCheckResult)
    assert after.status == HealthStatus.HEALTHY


@pytest.mark.asyncio
async def test_health_check_all_only_covers_resolved_providers(registry: ProviderRegistry):
    registry.register(ProviderCategory.LLM, "mock", provider_cls=MockLLMProvider)
    assert await registry.health_check_all() == {}
    await registry.resolve(ProviderCategory.LLM, "mock")
    results = await registry.health_check_all()
    assert "llm:mock" in results


def test_dependency_graph_detects_missing_dependency(registry: ProviderRegistry):
    registry.register(
        ProviderCategory.AGENT, "coordinator", provider_cls=MockLLMProvider, depends_on=("missing-provider",)
    )
    problems = registry.validate_dependencies()
    assert any("missing-provider" in p for p in problems)


def test_dependency_graph_detects_cycle(registry: ProviderRegistry):
    registry.register(ProviderCategory.LLM, "a", provider_cls=MockLLMProvider, depends_on=("llm:b",))
    registry.register(ProviderCategory.LLM, "b", provider_cls=MockLLMProvider, depends_on=("llm:a",))
    problems = registry.validate_dependencies()
    assert any("cycle" in p.lower() for p in problems)


@pytest.mark.asyncio
async def test_shutdown_all_clears_cache(registry: ProviderRegistry):
    registry.register(ProviderCategory.LLM, "mock", provider_cls=MockLLMProvider)
    instance = await registry.resolve(ProviderCategory.LLM, "mock")
    assert instance.is_initialized
    await registry.shutdown_all()
    assert not instance.is_initialized
    assert await registry.health_check_all() == {}
